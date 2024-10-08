# Start with a minimal CUDA 12 base image
FROM nvidia/cuda:12.3.1-base-ubuntu22.04

# Install Python and necessary tools
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
# Install Python 3.12 using uv
RUN uv python install python==3.12

# Set up the working directory
WORKDIR /app

# Copy the project files
COPY pyproject.toml uv.lock ./
COPY src ./src

# Install project dependencies using uv (only main dependencies)
RUN uv sync --no-dev --frozen

# Download and save the Cellpose model to the image
RUN mkdir -p /root/.cellpose/models && \
    uv run python3 -c "from cellpose import models; models.CellposeModel(model_type='cyto3', pretrained_model='/root/.cellpose/models/cyto3')"

# Set the entrypoint to python
ENTRYPOINT ["uv", "run"]

# Set the default command to main.py in the src directory (can be overridden)
CMD ["src.main.py"]