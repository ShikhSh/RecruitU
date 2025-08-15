# User Tile UI

This project is a React application that displays user information in a tile format. Each tile shows basic information about a user, and clicking on a tile reveals more detailed information.

## Project Structure

```
user-tile-ui
├── public
│   └── index.html          # Main HTML entry point
├── src
│   ├── components
│   │   ├── UserTile.tsx    # Component for displaying user tiles
│   │   └── UserDetail.tsx   # Component for displaying detailed user information
│   ├── data
│   │   └── users.json      # Mock data source for user information
│   ├── App.tsx             # Main application component
│   └── index.tsx           # Entry point of the React application
├── package.json            # npm configuration file
├── tsconfig.json           # TypeScript configuration file
└── README.md               # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd user-tile-ui
   ```

2. **Install dependencies:**
   ```
   npm install
   ```

3. **Run the application:**
   ```
   npm start
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000` to view the application.

## Usage

- The application displays a list of users in a tile format.
- Click on a user tile to view more detailed information about the user.
- The user data is sourced from the `src/data/users.json` file.

## Contributing

Feel free to submit issues or pull requests for any improvements or bug fixes.