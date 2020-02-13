package p

import (
	"fmt"
	"context"
	"log"
	"net/http"
	"bytes"
)

type PubSubMessage struct {
	Data []byte `json:"data"`
}

// HelloPubSub consumes a Pub/Sub message.
func HelloPubSub(ctx context.Context, m PubSubMessage) error {
	log.Println(string(m.Data))
    newData := m.Data
	response, err := http.Post("http://13.233.127.38:5000/h", "application/json", bytes.NewBuffer(newData))
	if err !=nil{
		fmt.Println(response)
    }else{
        log.Println("log for function")
    }
	return nil
}