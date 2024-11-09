# Real Estate API

## Overview
This project is a simple API for managing real estate products. It is built using FastAPI, a modern web framework for building APIs with Python 3.7+ based on standard Python type hints.

Sure, here is a README file for your project:

## Setup

### Prerequisites
- Python 3.7+
- Docker

### Installation
1. Clone the repository:
   ```sh

   ```

2. Set up the environment variables in a `.env` file:
   ```env
   POSTGRE_URL=your_postgres_url
   POSTGRES_USERNAME=your_postgres_username
   POSTGRES_PASSWORD=your_postgres_password
   POSTGRES_DB=your_postgres_db
   ```

3. Build and run the Docker containers:
   ```sh
   docker-compose -f docker/docker-compose.yml up --build
   ```

## Usage

### Running the API
To run the API, use the following command:
```sh
uvicorn api.main:app --reload
```

### Endpoints

#### Get Products
- **URL**: `/api/products`
- **Method**: `GET`
- **Query Parameters**:
  - `limit`: int
  - `category`: str
  - `dist`: str
  - `city`: str
  - `q`: str
  - `lowest_price`: int
  - `highest_price`: int
  - `lat_tl`: float
  - `long_tl`: float
  - `lat_br`: float
  - `long_br`: float
  - `offset`: int
- **Response**: List of products matching the filters.

#### Get Product
- **URL**: `/api/product`
- **Method**: `GET`
- **Query Parameters**:
  - `id`: str
- **Response**: Details of the product with the specified ID.

## Example Requests

### Get Products
```sh
curl -X GET "http://localhost:9292/api/products?limit=10&category=apartment&city=HaNoi&lowest_price=100000&highest_price=200000&lat_tl=21.036&long_tl=105.784&lat_br=20.998&long_br=105.848&offset=0"
```

### Get Product
```sh
curl -X GET "http://localhost:9292/api/product?id=12345"
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License
This project is licensed under the MIT License.
