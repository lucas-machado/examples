package main

import (
	"context"
	"encoding/binary"
	"fmt"
	"log"
	"math" // Necessário para converter bits de float corretamente
	"time"

	// Ajuste este import para o caminho onde você gerou seus .pb.go
	pb "triton-client/proto"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

func main() {
	serverAddr := "localhost:8001" // Triton gRPC roda na 8001 por padrão (não 8000)

	// 1. FIX: grpc.Dial -> grpc.NewClient (Nova API)
	conn, err := grpc.NewClient(serverAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("Failed to connect to server: %v", err)
	}
	defer conn.Close()

	client := pb.NewGRPCInferenceServiceClient(conn)

	// Dados de exemplo (1 cliente, 10 features)
	features := []float32{35.0, 5000.0, 750.0, 5.0, 1.0, 0.0, 2.0, 1.0, 0.0, 42.0}

	// Preparar o buffer de bytes (10 floats * 4 bytes cada = 40 bytes)
	inputData := make([]byte, len(features)*4)

	for i, f := range features {
		// 2. FIX: Usar Float32bits para preservar o valor decimal no formato binário
		bits := math.Float32bits(f)
		binary.LittleEndian.PutUint32(inputData[i*4:], bits)
	}

	// 3. FIX: Estrutura do Request para modo RAW
	request := &pb.ModelInferRequest{
		ModelName:    "credit_score_model",
		ModelVersion: "1",

		// Metadados do Tensor (Descreve O QUE é o dado)
		Inputs: []*pb.ModelInferRequest_InferInputTensor{
			{
				Name:     "input__0", // Deve bater com o config.pbtxt (ou usar nome padrão do XGBoost)
				Datatype: "FP32",
				Shape:    []int64{1, 10},
				// Note: O campo "Contents" fica VAZIO quando usamos RawInputContents
			},
		},

		// Os dados reais vão aqui (Lista de bytes, um []byte para cada input)
		RawInputContents: [][]byte{inputData},
	}

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	start := time.Now()
	response, err := client.ModelInfer(ctx, request)
	if err != nil {
		log.Fatalf("Failed to infer: %v", err)
	}
	elapsed := time.Since(start)

	// 4. FIX: Ler a resposta Raw e converter de volta para Float
	if len(response.RawOutputContents) > 0 {
		outputBytes := response.RawOutputContents[0]

		// O XGBoost geralmente retorna probabilidades (floats).
		// Precisamos converter os bytes brutos de volta para float32.
		bits := binary.LittleEndian.Uint32(outputBytes)
		probability := math.Float32frombits(bits)

		fmt.Printf("Inference time: %v\n", elapsed)
		fmt.Printf("Credit Score Probability: %f\n", probability)
	} else {
		fmt.Println("No raw output received.")
	}
}
