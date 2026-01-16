// This file is a consolidated example of a Hermetic Integration Test setup in Go.
// It combines the test infrastructure (TestMain, Embedded Postgres) with a concrete
// integration test example (`TestUpdateDisplayName_Success`).
//
// Highlights:
// 1. Uses an embedded Postgres instance for completely isolated, hermetic tests.
// 2. `TestMain` manages the DB lifecycle: starts once, runs all tests, stops.
// 3. `resetTestDB` provides fast isolation by TRUNCATING tables between tests (instead of restarting DB).
// 4. Demonstrates a full API integration test flow: Setup -> Create User -> Update -> Verify.
//
// Note: This file assumes it is part of the `server` package where `NewServer`,
// `Server` struct, and Handlers are defined.

package server

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"sort"
	"testing"
	"time"

	embeddedpostgres "github.com/fergusstrange/embedded-postgres"
	"github.com/jackc/pgx/v5/pgxpool"
)

// Shared test infrastructure globals
var (
	sharedDB   *embeddedpostgres.EmbeddedPostgres
	sharedPool *pgxpool.Pool
	sharedDSN  string
)

// TestMain manages the lifecycle of a single embedded Postgres instance for all tests.
// This dramatically speeds up test execution by avoiding DB startup/shutdown per test.
func TestMain(m *testing.M) {
	port := uint32(54339)
	dbName := "prota"
	user := "postgres"
	pass := "postgres"

	// Configure the embedded database
	sharedDB = embeddedpostgres.NewDatabase(embeddedpostgres.DefaultConfig().
		Port(port).
		Database(dbName).
		Username(user).
		Password(pass),
	)

	// Start the database
	if err := sharedDB.Start(); err != nil {
		// Try stopping first in case of leftover from crashed test
		_ = sharedDB.Stop()
		if err := sharedDB.Start(); err != nil {
			log.Fatalf("failed to start embedded postgres: %v", err)
		}
	}

	sharedDSN = fmt.Sprintf("postgresql://%s:%s@localhost:%d/%s?sslmode=disable", user, pass, port, dbName)

	// Connect to the DB
	ctx := context.Background()
	cfg, err := pgxpool.ParseConfig(sharedDSN)
	if err != nil {
		_ = sharedDB.Stop()
		log.Fatalf("parse dsn: %v", err)
	}
	cfg.MaxConns = 20 // Higher for parallel tests

	pool, err := pgxpool.NewWithConfig(ctx, cfg)
	if err != nil {
		_ = sharedDB.Stop()
		log.Fatalf("connect pool: %v", err)
	}
	sharedPool = pool

	// Run migrations ONCE for the entire test suite
	if err := runMigrationsOnce(pool); err != nil {
		pool.Close()
		_ = sharedDB.Stop()
		log.Fatalf("migrations failed: %v", err)
	}

	// Run all tests in the package
	code := m.Run()

	// Cleanup
	pool.Close()
	if err := sharedDB.Stop(); err != nil {
		log.Printf("warning: failed to stop embedded postgres: %v", err)
	}

	os.Exit(code)
}

// startTestDB resets the shared database (TRUNCATE) and returns the DSN.
// It is called by each individual test to ensure a clean slate.
func startTestDB(t *testing.T) (string, func()) {
	t.Helper()
	resetTestDB(t)              // Truncate tables for isolation
	return sharedDSN, func() {} // No-op cleanup; DB lifecycle managed by TestMain
}

// migrateSQL returns the shared pool. Migrations are run once by TestMain.
func migrateSQL(t *testing.T, dsn string) *pgxpool.Pool {
	t.Helper()
	return sharedPool
}

// resetTestDB truncates all data tables and reseeds required data.
// This is MUCH faster than restarting the database.
func resetTestDB(t *testing.T) {
	t.Helper()
	ctx := context.Background()

	// Small delay to allow any background goroutines from previous test to complete
	time.Sleep(50 * time.Millisecond)

	// Truncate all user data tables (order matters for FK constraints, use CASCADE)
	_, err := sharedPool.Exec(ctx, `
		TRUNCATE TABLE 
			users,
			user_balance,
			gift_cards,
			gift_card_types,
			reward_ledger,
			user_achievements,
			user_redirects,
			device_tokens,
			user_links,
			spend_ledger,
			iap_products
		RESTART IDENTITY CASCADE
	`)
	if err != nil {
		t.Fatalf("truncate tables: %v", err)
	}

	// Reseed static data (like IAP products) that was lost during truncation
	_, err = sharedPool.Exec(ctx, `
		INSERT INTO iap_products (product_id, coins) VALUES
			('com.prota.rewards.coins.small', 400),
			('com.prota.rewards.coins.medium', 1500),
			('com.prota.rewards.coins.large', 2800)
		ON CONFLICT (product_id) DO NOTHING
	`)
	if err != nil {
		t.Fatalf("reseed iap_products: %v", err)
	}
}

// runMigrationsOnce applies all SQL migrations to the shared database.
func runMigrationsOnce(pool *pgxpool.Pool) error {
	ctx := context.Background()

	dir, err := findMigrationsDirSimple()
	if err != nil {
		// If running as a standalone snippet without migrations dir, you might mock this.
		// For now, we return error to fail fast if env is wrong.
		return err
	}

	entries, err := os.ReadDir(dir)
	if err != nil {
		return fmt.Errorf("read migrations: %w", err)
	}

	files := make([]string, 0, len(entries))
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		if filepath.Ext(e.Name()) == ".sql" {
			files = append(files, filepath.Join(dir, e.Name()))
		}
	}

	sort.Slice(files, func(i, j int) bool {
		var numI, numJ int
		_, _ = fmt.Sscanf(filepath.Base(files[i]), "V%d__", &numI)
		_, _ = fmt.Sscanf(filepath.Base(files[j]), "V%d__", &numJ)
		return numI < numJ
	})

	for _, f := range files {
		b, err := os.ReadFile(f)
		if err != nil {
			return fmt.Errorf("read %s: %w", f, err)
		}
		if _, err := pool.Exec(ctx, string(b)); err != nil {
			return fmt.Errorf("migrate %s: %w", f, err)
		}
	}
	return nil
}

// findMigrationsDirSimple locates the migrations directory.
func findMigrationsDirSimple() (string, error) {
	candidates := []string{
		filepath.Join("..", "..", "migrations"),
		filepath.Join("..", "migrations"),
		"migrations",
	}

	for _, c := range candidates {
		if st, err := os.Stat(c); err == nil && st.IsDir() {
			return c, nil
		}
	}
	return "", fmt.Errorf("migrations dir not found")
}

// --- The Integration Test ---

// TestUpdateDisplayName_Success tests the full flow of updating a user's display name.
// It verifies the update persists to the DB and is reflected in subsequent reads.
func TestUpdateDisplayName_Success(t *testing.T) {
	if testing.Short() {
		t.Skip("short")
	}

	// 1. Setup Isolated Test DB
	dsn, stop := startTestDB(t)
	defer stop()
	pool := migrateSQL(t, dsn)

	// 2. Initialize the Server with the test DB
	// Note: NewServer and handlers are defined in the main application code (not shown here).
	s := NewServer(pool, nil) // nil for PushSender

	// 3. Create an Anonymous User to act as the test subject
	w := httptest.NewRecorder()
	req := httptest.NewRequest(http.MethodPost, "/v1/users/anonymous", nil)
	s.CreateAnonymousUserHandler(w, req) // Handler creates user in DB
	var anon struct {
		UserID      string `json:"user_id"`
		AccessToken string `json:"access_token"`
	}
	_ = json.Unmarshal(w.Body.Bytes(), &anon)

	// 4. Execute the Action: Update Display Name
	body, _ := json.Marshal(map[string]string{"display_name": "PlayerOne"})
	w = httptest.NewRecorder()
	req = httptest.NewRequest(http.MethodPost, "/v1/users/me/display-name", bytes.NewReader(body))
	req.Header.Set("Authorization", "Bearer "+anon.AccessToken) // Auth Header required
	req.Header.Set("Content-Type", "application/json")

	s.UpdateDisplayNameHandler(w, req) // Call the handler directly

	// 5. Verify Response Code
	if w.Code != http.StatusOK {
		t.Fatalf("update display name: %d %s", w.Code, w.Body.String())
	}

	// 6. Verify Response Body
	var resp struct {
		DisplayName string `json:"display_name"`
	}
	_ = json.Unmarshal(w.Body.Bytes(), &resp)
	if resp.DisplayName != "PlayerOne" {
		t.Fatalf("expected 'PlayerOne' got '%s'", resp.DisplayName)
	}

	// 7. Verify Persistence (Side Effect)
	// Fetch the user state from a different endpoint to ensure DB was updated
	w = httptest.NewRecorder()
	req = httptest.NewRequest(http.MethodGet, "/v1/users/state", nil)
	req.Header.Set("Authorization", "Bearer "+anon.AccessToken)
	s.UserStateHandler(w, req)

	var state struct {
		DisplayName string `json:"display_name"`
	}
	_ = json.Unmarshal(w.Body.Bytes(), &state)
	if state.DisplayName != "PlayerOne" {
		t.Fatalf("state display name: expected 'PlayerOne' got '%s'", state.DisplayName)
	}
}
