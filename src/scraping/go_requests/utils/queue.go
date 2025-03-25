package utils

// enqueue adds an element to the end of the queue.
func Push[T any](queue []T, element T) []T {
	queue = append(queue, element)
	return queue
}

// dequeue removes the first element from the queue and returns it along with the updated queue.
func Pop[T any](queue []T) (T, []T) {
	element := queue[0]
	if len(queue) == 1 {
		var tmp []T
		return element, tmp
	}
	return element, queue[1:]
}
