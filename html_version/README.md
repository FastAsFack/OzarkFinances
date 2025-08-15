# Ozark Finances - HTML Version

This is a static HTML version of the Ozark Finances Flask application with a unified color scheme across all pages.

## Features

- **Unified Color Scheme**: All pages use consistent CSS variables for colors
- **Responsive Design**: Mobile-first approach with responsive layouts
- **Dark Theme**: Professional dark theme optimized for extended use
- **Consistent Typography**: JetBrains Mono font for a modern, readable interface
- **No JavaScript Dependencies**: Pure HTML/CSS implementation

## File Structure

```
html_version/
├── css/
│   └── style.css          # Unified stylesheet with CSS variables
├── index.html             # Dashboard page
├── invoices.html          # Invoice management
├── withdraws.html         # Withdraw management
├── debt.html              # Debt tracking
├── important_info.html    # Financial information & alerts
├── card_variations.html   # Design showcase
└── README.md              # This file
```

## Color Scheme

The application uses CSS custom properties for consistent theming:

### Primary Colors
- `--bg-dark: #2b2b2b` - Main background
- `--control-dark: #211a1a` - Cards, forms, navbar
- `--text-light: #ffffff` - Primary text color
- `--text-muted: #aaa` - Secondary text

### Accent Colors
- `--primary-color: #0d6efd` - Primary actions and links
- `--success-color: #198754` - Success states and positive values
- `--danger-color: #dc3545` - Danger states and negative values
- `--warning-color: #ffc107` - Warning states
- `--info-color: #0dcaf0` - Information states

### Border & Overlay Colors
- `--border-color: #444` - Standard borders
- `--hover-color: #3a3a3a` - Hover states
- Various rgba overlays for subtle backgrounds

## Pages Overview

### 1. Dashboard (index.html)
- Financial overview with key metrics
- Recent invoices and withdraws
- Quick navigation to other sections

### 2. Invoices (invoices.html)
- Add new invoices
- Filter and search functionality
- Comprehensive invoice table with VAT calculations

### 3. Withdraws (withdraws.html)
- Track business withdraws
- Monthly summaries
- Withdraw history table

### 4. Debt Management (debt.html)
- Track multiple debt accounts
- Payment planning recommendations
- Debt-to-income ratio calculations

### 5. Important Information (important_info.html)
- Financial health overview
- Tax information (Dutch system)
- Financial goals and targets
- Important contacts

### 6. Card Variations (card_variations.html)
- Showcase of different card designs
- Color scheme documentation
- Design implementation examples

## Benefits of This Implementation

1. **Consistency**: All pages use the same color variables and styling patterns
2. **Maintainability**: Changes to colors can be made in one place (CSS variables)
3. **Performance**: No external dependencies beyond Font Awesome icons
4. **Accessibility**: Consistent contrast ratios and semantic HTML
5. **Responsive**: Works well on desktop, tablet, and mobile devices

## Usage

Simply open any HTML file in a web browser. All pages are interconnected through the navigation menu.

## Customization

To change the color scheme:
1. Modify the CSS variables in the `:root` selector in `css/style.css`
2. All pages will automatically update to use the new colors

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid and Flexbox support required
- CSS Custom Properties support required

## Future Enhancements

- Add JavaScript for interactive features
- Implement local storage for data persistence
- Add print stylesheets
- Include chart visualizations
- Add form validation
