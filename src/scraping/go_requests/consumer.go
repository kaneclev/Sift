package consumer
import (
	"os"
	"encoding/json"
)

type RequestEncoding struct {
	ID int `json:"id"`
	URL string `json:"url"`
	Alias string `json:"alias"`
}
type RCollection struct {
	requests []RequestEncoding
}
type Consumer interface {
	files 
	findRequests()
}

func (cons *RCollection) findRequests(dir string) {
	cons 
}