APP_NAME = siftrequests
BUILD_DIR = bin
MAIN = main
PROJ_DIR = ./src/scraping/go_requests/$(MAIN).go

# Ensure the bin directory exists
$(BUILD_DIR):
	mkdir $(BUILD_DIR)

build: $(BUILD_DIR)
	go build -o $(BUILD_DIR)/$(APP_NAME).exe $(PROJ_DIR)

run: build
	$(BUILD_DIR)/$(APP_NAME).exe

clean:
	rm -rf $(BUILD_DIR)
