# Frontend for Backend CRM

A React-based frontend for the CRM backend with geographic visualization using react-simple-maps.

## Features

- 📍 Interactive US map with debtor locations
- ☎️ Call logging and history
- 📧 Email logging and tracking
- 💰 Debt/amount owed visualization
- 🔍 Search and filter functionality
- 📊 Statistics and analytics dashboard
- 🎵 Voice integration
- 🔐 JWT authentication

## Tech Stack

- React 18+
- TypeScript
- TailwindCSS
- react-simple-maps
- Axios
- React Router v6

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

```bash
# Clone repository
git clone https://github.com/mc8608849-hub/frontend-crm.git
cd frontend-crm

# Install dependencies
npm install
```

### Configuration

Create `.env.local`:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=10000
```

### Development

```bash
# Start development server
npm start

# Server runs at http://localhost:3000
```

### Build

```bash
# Create production build
npm run build

# Serve production build locally
npm run serve
```

## Project Structure

```
frontend-crm/
├── src/
│   ├── components/
│   │   ├── Map/
│   │   │   ├── USMap.tsx
│   │   │   └── MapMarker.tsx
│   │   ├── Dashboard/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Statistics.tsx
│   │   │   └── RecentCalls.tsx
│   │   ├── People/
│   │   │   ├── PeopleList.tsx
│   │   │   ├── PersonForm.tsx
│   │   │   └── PersonDetail.tsx
│   │   ├── Calls/
│   │   │   ├── CallLog.tsx
│   │   │   ├── CallForm.tsx
│   │   │   └── CallHistory.tsx
│   │   └── Auth/
│   │       ├── Login.tsx
│   │       └── ProtectedRoute.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── types.ts
│   ├── App.tsx
│   └── index.tsx
├── public/
├── package.json
└── tailwind.config.js
```

## API Integration

### Authentication

```typescript
import { api } from './services/api';

// Login
const { data } = await api.post('/api/auth/login', {
  username: 'admin',
  password: 'password'
});

// Get current user
const user = await api.get('/api/auth/me');
```

### People/Debtors

```typescript
// Get all people
const people = await api.get('/api/people/');

// Get specific person
const person = await api.get(`/api/people/${personId}`);

// Create person
const newPerson = await api.post('/api/people/', personData);

// Update person
const updated = await api.put(`/api/people/${personId}`, updatedData);

// Delete person
await api.delete(`/api/people/${personId}`);
```

### Call Logs

```typescript
// Get all calls
const calls = await api.get('/api/calls/');

// Get calls for person
const personCalls = await api.get(`/api/calls/person/${personId}`);

// Create call log
const callLog = await api.post('/api/calls/', callData);

// Update call
const updated = await api.put(`/api/calls/${callId}`, updatedData);
```

## Map Component

### Basic Usage

```tsx
import { USMap } from './components/Map/USMap';

function App() {
  const people = [
    { id: 1, name: 'John Doe', lat: 34.0522, lon: -118.2437, state: 'CA' },
    { id: 2, name: 'Jane Smith', lat: 40.7128, lon: -74.0060, state: 'NY' }
  ];

  return <USMap people={people} />;
}
```

### Marker Customization

```tsx
<USMap 
  people={people}
  onMarkerClick={(person) => console.log(person)}
  markerColor={(person) => person.amount_owed > 5000 ? 'red' : 'blue'}
/>
```

## Dashboard Features

### Statistics Widget

Shows:
- Total debtors
- Total amount owed
- Recent calls
- Call success rate

### Recent Activity

- Latest calls
- Recent emails
- New contacts
- Status updates

## Development Tips

### Environment Variables

```env
# Backend API
REACT_APP_API_URL=http://localhost:8000

# Debug
REACT_APP_DEBUG=true

# Feature flags
REACT_APP_ENABLE_ANALYTICS=true
```

### Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- Map.test.tsx
```

### Code Quality

```bash
# Run ESLint
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

## Deployment

### Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Netlify

```bash
# Build
npm run build

# Deploy to Netlify
netlify deploy --prod --dir=build
```

### Docker

```bash
docker build -t frontend-crm .
docker run -p 3000:3000 frontend-crm
```

## Troubleshooting

### API Connection Issues

```typescript
// Check API URL
console.log(process.env.REACT_APP_API_URL);

// Test connection
fetch(`${process.env.REACT_APP_API_URL}/api/auth/me`)
  .then(r => console.log('Connected'))
  .catch(e => console.error('Connection failed:', e));
```

### Map Not Rendering

- Ensure react-simple-maps is installed
- Check browser console for errors
- Verify coordinate data format (lat/lon)

### Authentication Issues

- Check token is saved in localStorage
- Verify token format in Authorization header
- Check token expiration

## Performance

### Optimization Tips

1. **Lazy load components**
   ```tsx
   const Map = lazy(() => import('./components/Map/USMap'));
   ```

2. **Memoize expensive components**
   ```tsx
   export const PeopleList = memo(PeopleListComponent);
   ```

3. **Optimize API calls**
   - Use pagination
   - Implement caching
   - Debounce search

### Bundle Size

```bash
# Analyze bundle
npm run analyze
```

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## License

MIT
