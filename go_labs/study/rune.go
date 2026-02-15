package main

import "fmt"

func main() {
	s := "GoLang1.21"

	runes := []rune(s)

	fmt.Printf("%v", runes)

	a, b := 0, 1
	sum := 0

	for a < len(runes)  {
		sum += int(runes[a])
		a = b
		b = a + b
	}

	fmt.Printf("%v", sum)
}