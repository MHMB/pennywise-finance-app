# Pennywise Finance Frontend

A modern React frontend for the Pennywise Finance application, built with TypeScript, Tailwind CSS, and comprehensive internationalization support.

## Features

- **Authentication**: Secure login/register with Django REST Framework integration
- **Dashboard**: Comprehensive financial overview with real-time data
- **Transaction Management**: Add, edit, delete transactions with CSV import/export
- **Budget Management**: Create and track budgets with visual progress indicators
- **Reports**: Multiple report types with filtering and export capabilities
- **Settings**: User profile management and notification preferences
- **Internationalization**: Full support for English and Persian (RTL)
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Dark Mode**: Theme switching capability

## Tech Stack

- **React 18** with TypeScript
- **React Router** for navigation
- **React Query** for data fetching and caching
- **React Hook Form** for form management
- **Tailwind CSS** for styling
- **React Hot Toast** for notifications
- **React Dropzone** for file uploads
- **Chart.js & Recharts** for data visualization
- **i18next** for internationalization

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Docker

The frontend is also configured to run with Docker:

```bash
docker-compose up frontend
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout/         # Layout components (Header, Sidebar)
│   └── UI/             # Basic UI components
├── contexts/           # React contexts (Auth, Theme, Language)
├── hooks/              # Custom React hooks
├── pages/              # Page components
│   ├── Auth/           # Login/Register pages
│   ├── Dashboard/      # Dashboard page
│   ├── Transactions/   # Transaction management
│   ├── Budgets/        # Budget management
│   ├── Reports/        # Reports and analytics
│   └── Settings/       # User settings
├── services/           # API service layer
├── styles/             # Global styles and CSS
└── utils/              # Utility functions and i18n config
```

## Key Features Implementation

### Authentication
- Token-based authentication with automatic token refresh
- Protected routes with authentication guards
- User registration and login forms with validation

### CSV Import System
- Drag-and-drop CSV file upload
- Robust error handling and validation
- Automatic category detection and duplicate prevention
- Progress feedback during import process

### Budget Management
- Visual budget status indicators
- Real-time spending tracking
- Budget alerts and recommendations
- Multiple time periods (weekly, monthly, yearly)

### Internationalization
- Complete English and Persian translations
- RTL layout support for Persian
- Language switching with persistence
- Proper date and number formatting

### Responsive Design
- Mobile-first approach
- Tablet and desktop optimizations
- Touch-friendly interface elements
- Print-friendly layouts

## API Integration

The frontend integrates with the Django REST Framework backend through a centralized API service (`apiService.ts`) that handles:

- Authentication token management
- Request/response interceptors
- Error handling
- Automatic retries and caching

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Environment Variables

- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000/api)

## Contributing

1. Follow the existing code structure and naming conventions
2. Use TypeScript for all new components
3. Add proper error handling and loading states
4. Include translations for new text content
5. Test responsive design on multiple screen sizes

## License

This project is licensed under the MIT License.