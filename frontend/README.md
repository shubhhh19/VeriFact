# News Validator Agent - Frontend

A modern React frontend for the News Validator Agent, built with Vite, TypeScript, and Tailwind CSS.

## Features

- **Modern UI**: Clean, responsive design with Tailwind CSS
- **TypeScript**: Full type safety and better developer experience
- **Real-time Validation**: Submit news article URLs for AI-powered validation
- **Results Display**: View credibility scores, claims, and contradictions
- **API Integration**: Ready to connect with the FastAPI backend

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Development**: ESLint, TypeScript

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser to `http://localhost:3000`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Header.tsx      # Application header
│   │   ├── Footer.tsx      # Application footer
│   │   ├── NewsValidator.tsx # Main validation interface
│   │   ├── ValidationForm.tsx # Form for submitting URLs
│   │   └── ValidationResults.tsx # Results display
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # Application entry point
│   └── index.css           # Global styles with Tailwind
├── public/                 # Static assets
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

## API Integration

The frontend is configured to proxy API requests to the backend:

- Development: Requests to `/api/*` are proxied to `http://localhost:8000`
- Production: Update the API base URL in your environment

## Development

### Adding New Components

1. Create new components in `src/components/`
2. Use TypeScript interfaces for props
3. Follow the existing styling patterns with Tailwind CSS

### Styling

- Use Tailwind CSS utility classes
- Custom components are defined in `src/index.css`
- Follow the design system with primary colors and spacing

### State Management

Currently using React hooks for local state. For more complex state management, consider:

- React Context API
- Zustand
- Redux Toolkit

## Deployment

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Deployment Options

- **Vercel**: Connect your repository for automatic deployments
- **Netlify**: Deploy from the `dist/` directory
- **Docker**: Use the provided Dockerfile

## Contributing

1. Follow the existing code style
2. Add TypeScript types for all props and state
3. Test your changes locally
4. Update documentation as needed

## License

This project is licensed under the MIT License. 