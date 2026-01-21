package main

import (
	"fmt"
	"log"
	"sync"
	"sync/atomic"
	"time"

	"net/http"
	_ "net/http/pprof"
)

var byteCounter int64 = 0

func worker(id int, jobs <-chan int, results chan<- string, wg *sync.WaitGroup) {
	defer wg.Done()
	for j := range jobs {
		fmt.Printf("Worker %d started job %d\n", id, j)
		time.Sleep(time.Second)
		fmt.Printf("Worker %d finished job %d\n", id, j)

		atomic.AddInt64(&byteCounter, 1)

		results <- fmt.Sprintf("Worker %d finished job %d", id, j)
	}
}

func main() {
	go func() {
		log.Println(http.ListenAndServe(":6060", nil))
	}()

	jobs := make(chan int, 100)
	results := make(chan string, 100)
	wg := sync.WaitGroup{}

	for w := 1; w <= 3; w++ {
		wg.Add(1)
		go worker(w, jobs, results, &wg)
	}

	for j := 1; j <= 100; j++ {
		jobs <- j
	}

	close(jobs)
	wg.Wait()
	close(results)

	for r := range results {
		fmt.Println(r)
	}

	fmt.Printf("Byte counter: %d\n", atomic.LoadInt64(&byteCounter))
}
