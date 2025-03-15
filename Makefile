APP_NAME = siftrequests
BUILD_DIR = bin
MAIN = main
PROJ_DIR = ./src/scraping/go_requests

# Ensure the bin directory exists
$(BUILD_DIR):
	mkdir $(BUILD_DIR)

build: $(BUILD_DIR)
	cd $(PROJ_DIR) && go build -o ../../../$(BUILD_DIR)/$(APP_NAME).exe

run: build
	$(BUILD_DIR)/$(APP_NAME).exe --finput to_consume

clean:
	rm -rf $(BUILD_DIR)
