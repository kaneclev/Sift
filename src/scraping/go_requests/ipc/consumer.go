package ipc

type RequestEncoding struct {
	ID    int    `json:"id"`
	URL   string `json:"url"`
	Alias string `json:"alias"`
}
type RCollection struct {
	requests []RequestEncoding
}
type Consumer interface {
	findRequests()
}

func (col *RCollection) findRequests(dir string) {
	col.requests = []RequestEncoding{}
}
