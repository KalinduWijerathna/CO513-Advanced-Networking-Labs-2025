# Lab 5: QoS Algorithms Leaky vs Token Bucket Using Server-Client Architecture

## Lab Tasks

### 1. Setup and Dependencies  
- Update and install dependencies:
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip ffmpeg
  pip3 install opencv-python ffmpeg-python psutil
  ````

---

### 2. Part 1: Initial Testing

Run the following scripts **in parallel, in separate terminals**:

* `video_server_h264.py`
* `video_client_h264.py`

**Changing resolution:**

* Select the appropriate sample video in the server file:

  * `sample_270p.mp4`
  * `sample_720p.mp4`
  * `sample_1080p.mp4`
* Change the width and height settings in the client file accordingly:

  ```python
  WIDTH, HEIGHT = 480, 270    # 270p
  WIDTH, HEIGHT = 1280, 720   # 720p
  WIDTH, HEIGHT = 1920, 1080  # 1080p  
  ``` 

---


### 3. Part 2: QoS Algorithms

#### Leaky Bucket Algorithm

Run **in parallel**:

* `leaky_bucket_server.py`
* `leaky_bucket_client.py`

#### Token Bucket Algorithm

Run **in parallel**:

* `token_bucket_server.py`
* `token_bucket_client.py`

---

### 4. Part 3: QoS Integration for Streaming (Token Bucket)

Run **in parallel**:

* `video_server_with_token_bucket_h264.py`
* `video_client_with_token_bucket_h264.py`

Then generate comparison plots:

    ```bash
    cd ./comparisons
    python3 noqos-vs-tokenbucket.py
    ```


---

## Experimentation and Analysis

### 1. TCP vs UDP Comparison

Run **in parallel**:

* `video_server_with_token_bucket_h264_udp.py`
* `video_client_with_token_bucket_h264_udp.py`

Generate comparison plots:

    ```bash
    cd ./comparisons
    python3 tcp-vs-udp-fortokenbucket.py
    ```

After generating plots for all three resolutions, run for full comparison:

    ```bash
    cd ./comparisons
    python3 tcp-vs-udp-fortokenbucket-varyingqualities-percentage.py
    ```

---

### 2. Latency Analysis

Run **in parallel**:

* `video_server_with_token_bucket_h264_indepth_latency.py`
* `video_client_with_token_bucket_h264_indepth_latency.py`

---

### 3. Encoding Efficiency

**i. H264:**

* `video_server_with_token_bucket_h264_log_all.py`
* `video_client_with_token_bucket_h264_log_all.py`

**ii. H265:**

* `video_server_with_token_bucket_h265_log_all.py`
* `video_client_with_token_bucket_h265_log_all.py`

**iii. VP9:**

* `video_server_with_token_bucket_vp9_log_all.py`
* `video_client_with_token_bucket_vp9_log_all.py`

Generate comparative analysis for each codec:

    ```bash
    cd ./comparisons
    python3 plot_all_for_codec.py <codec-name>
    ```

For overall comparative analysis between codecs:

    ```bash
    cd ./comparisons
    python3 plot_all_codecs.py
    ```

---

### 4. QoS Algorithm Evaluation

Run **in parallel**:

* `video_server_with_leaky_bucket_h264.py`
* `video_client_with_leaky_bucket_h264.py`

Modify resolution in scripts to generate logs (`.csv`) for all three resolutions.

For comparative analysis run:

    ```bash
    cd ./comparisons
    python3 leaky-vs-token.py
    ```

---

## Output Locations

* Individual plots saved in: `./plots`
* Comparative plots saved in: `./comparisons`
* Logs saved in: `./logs` (used for comparative plot generation)

---

## Notes

* Before running comparison scripts, verify the relevant `.csv` file names in `./logs`.
* Rename files if necessary to match the expected naming format used by comparison scripts.

---


