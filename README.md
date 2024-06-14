# Spatial Labs AI Engineer Take Home Assessment

## Setup

1. Install any necessary dependencies, such as Docker, Poetry, and direnv.
    - For playing audio on an Ubuntu distro, the following install worked for me:
        - `sudo apt-get install -y libasound2-dev libavcodec-extra portaudio19-dev python3-pyaudio`
    - For other systems, see https://www.askmarvin.ai/welcome/installation/#audio-features
2. Copy the `.env.example` file to `.env`, fill in your OPENAI_API_KEY, and adjust any other settings as needed
3. Run `poetry install` (or `make`)
4. Run `docker-compose up -d` to start the PostgreSQL database
5. Run the Jupyter notebook at `notebooks/agent.ipynb` to build and populate the vector index for the product catalog. This will use the `data/products.csv` and `data/augmented_products.csv` files if present. If you want to generate these files from scratch, delete them before running the notebook.
6. Run `make install` to install the Customer Assistant.
7. Run `make run` to start chatting with the Customer Assistant.

## Video Demo

![](./data/demo.gif)

