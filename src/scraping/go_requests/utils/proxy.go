package utils

import (
	"fmt"
	"math/rand"
	"os"
	"strconv"
)

func GetMaxNumProxies() int {
	max_num := os.Getenv("MAX_PROXIES")
	if max_num == "" {
		fmt.Printf("\n(!) Can't find field 'MAX_PROXIES' in the environment.")
		return -1
	}
	max_num_int, err := strconv.Atoi(max_num)
	if err != nil {
		fmt.Printf("\nCannot convert 'MAX_PROXIES' to an integer; given str to convert: %s, error: %s\n", max_num, err.Error())
		return -1
	}
	return max_num_int
}

func GetProxies(num int) []string {
	prox_prepend := "PROX"
	if num < 0 {
		num = GetMaxNumProxies()
		if num < 0 {
			return nil
		}
	}
	proxlist := make([]string, 0, num)
	for i := 1; i < num; i++ {
		currproxstring := prox_prepend + strconv.Itoa(i)
		prox := os.Getenv(currproxstring)
		if len(prox) == 0 {
			fmt.Printf("\n Warning: no proxy associated with key %s\n", currproxstring)
			continue
		}
		proxlist = append(proxlist, prox)
	}
	return proxlist
}

func GetRandProxy(plist []string) string {
	// Generate a random integer [0..99].
	if len(plist) < 1 {
		return ""
	}
	randomInt := rand.Intn(len(plist))
	return plist[randomInt]
}
