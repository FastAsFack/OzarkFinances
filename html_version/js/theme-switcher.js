// Theme Switcher JavaScript
class ThemeSwitcher {
    constructor() {
        this.themes = [
            {
                id: 'style',
                name: 'Original Dark',
                description: 'Classic professional theme',
                color: '#2b2b2b',
                file: 'css/style.css'
            },
            {
                id: 'theme-deep-blue',
                name: 'Deep Blue',
                description: 'Ocean-inspired calming theme',
                color: '#0f1419',
                file: 'css/theme-deep-blue.css'
            },
            {
                id: 'theme-purple-night',
                name: 'Purple Night',
                description: 'Rich and sophisticated',
                color: '#1a0d26',
                file: 'css/theme-purple-night.css'
            },
            {
                id: 'theme-forest-green',
                name: 'Forest Green',
                description: 'Nature-inspired relaxing',
                color: '#0d1f0d',
                file: 'css/theme-forest-green.css'
            },
            {
                id: 'theme-warm-amber',
                name: 'Warm Amber',
                description: 'Cozy and inviting',
                color: '#1f1611',
                file: 'css/theme-warm-amber.css'
            },
            {
                id: 'theme-slate-gray',
                name: 'Slate Gray',
                description: 'Modern and minimalist',
                color: '#0f172a',
                file: 'css/theme-slate-gray.css'
            },
            {
                id: 'theme-midnight-azure',
                name: 'Midnight Azure',
                description: 'Deep blue mystique',
                color: '#0a1118',
                file: 'css/theme-midnight-azure.css'
            },
            {
                id: 'theme-crimson-night',
                name: 'Crimson Night',
                description: 'Bold and passionate',
                color: '#1a0a0d',
                file: 'css/theme-crimson-night.css'
            },
            {
                id: 'theme-emerald-depths',
                name: 'Emerald Depths',
                description: 'Deep green tranquility',
                color: '#0a1a0d',
                file: 'css/theme-emerald-depths.css'
            },
            {
                id: 'theme-golden-dusk',
                name: 'Golden Dusk',
                description: 'Warm sunset vibes',
                color: '#1a1607',
                file: 'css/theme-golden-dusk.css'
            },
            {
                id: 'theme-violet-storm',
                name: 'Violet Storm',
                description: 'Electric purple energy',
                color: '#140a1a',
                file: 'css/theme-violet-storm.css'
            },
            {
                id: 'theme-copper-oxide',
                name: 'Copper Oxide',
                description: 'Industrial metallic feel',
                color: '#1a0f0a',
                file: 'css/theme-copper-oxide.css'
            },
            {
                id: 'theme-ocean-abyss',
                name: 'Ocean Abyss',
                description: 'Deep sea exploration',
                color: '#0a1518',
                file: 'css/theme-ocean-abyss.css'
            },
            {
                id: 'theme-neon-cyber',
                name: 'Neon Cyber',
                description: 'Futuristic matrix style',
                color: '#0a1a0a',
                file: 'css/theme-neon-cyber.css'
            },
            {
                id: 'theme-rose-gold',
                name: 'Rose Gold',
                description: 'Elegant pink metallic',
                color: '#1a0f12',
                file: 'css/theme-rose-gold.css'
            },
            {
                id: 'theme-mint-charcoal',
                name: 'Mint Charcoal',
                description: 'Fresh mint accent',
                color: '#0a1a15',
                file: 'css/theme-mint-charcoal.css'
            },
            {
                id: 'theme-steel-gray',
                name: 'Steel Gray',
                description: 'Industrial strength',
                color: '#12151a',
                file: 'css/theme-steel-gray.css'
            },
            {
                id: 'theme-burgundy-noir',
                name: 'Burgundy Noir',
                description: 'Wine-dark sophistication',
                color: '#1a0f12',
                file: 'css/theme-burgundy-noir.css'
            },
            {
                id: 'theme-forest-shadow',
                name: 'Forest Shadow',
                description: 'Deep woodland mystery',
                color: '#0d1b0f',
                file: 'css/theme-forest-shadow.css'
            },
            {
                id: 'theme-cosmic-purple',
                name: 'Cosmic Purple',
                description: 'Galactic deep space',
                color: '#0f0a1a',
                file: 'css/theme-cosmic-purple.css'
            },
            {
                id: 'theme-arctic-blue',
                name: 'Arctic Blue',
                description: 'Cool northern lights',
                color: '#0a1520',
                file: 'css/theme-arctic-blue.css'
            },
            {
                id: 'theme-amber-night',
                name: 'Amber Night',
                description: 'Warm golden glow',
                color: '#1a1507',
                file: 'css/theme-amber-night.css'
            },
            {
                id: 'theme-slate-storm',
                name: 'Slate Storm',
                description: 'Stormy gray skies',
                color: '#0f1419',
                file: 'css/theme-slate-storm.css'
            },
            {
                id: 'theme-mahogany-depths',
                name: 'Mahogany Depths',
                description: 'Rich wood tones',
                color: '#1a0c0a',
                file: 'css/theme-mahogany-depths.css'
            },
            {
                id: 'theme-indigo-mist',
                name: 'Indigo Mist',
                description: 'Mystical twilight',
                color: '#0d0f1a',
                file: 'css/theme-indigo-mist.css'
            },
            {
                id: 'theme-electric-lime',
                name: 'Electric Lime',
                description: 'Vibrant energy boost',
                color: '#0a1a0a',
                file: 'css/theme-electric-lime.css'
            }
        ];
        
        this.currentTheme = this.getSavedTheme() || 'style';
        this.isCollapsed = this.getSavedCollapsedState();
        this.customColors = this.getSavedCustomColors();
        this.init();
    }
    
    init() {
        this.createSwitcher();
        this.applyTheme(this.currentTheme);
        this.attachEventListeners();
    }
    
    createSwitcher() {
        // Check if switcher already exists
        if (document.querySelector('.theme-switcher')) {
            return;
        }
        
        const switcher = document.createElement('div');
        switcher.className = `theme-switcher ${this.isCollapsed ? 'collapsed' : ''}`;
        
        const toggle = document.createElement('button');
        toggle.className = 'theme-switcher-toggle';
        toggle.innerHTML = '<i class="fas fa-palette"></i>';
        toggle.title = 'Toggle Theme Switcher';
        
        const content = document.createElement('div');
        content.className = 'theme-switcher-content';
        
        const title = document.createElement('h6');
        title.textContent = 'Choose Theme:';
        content.appendChild(title);
        
        // Create scrollable container for theme options
        const optionsContainer = document.createElement('div');
        optionsContainer.className = 'theme-options-container';
        
        this.themes.forEach(theme => {
            const option = document.createElement('div');
            option.className = `theme-option ${theme.id === this.currentTheme ? 'active' : ''}`;
            option.dataset.theme = theme.id;
            
            option.innerHTML = `
                <span class="color-preview" style="background: ${theme.color};"></span>
                <div>
                    <div class="theme-name">${theme.name}</div>
                    <div class="theme-description">${theme.description}</div>
                </div>
            `;
            
            optionsContainer.appendChild(option);
        });
        
        content.appendChild(optionsContainer);
        
        // Add custom color picker section
        this.createCustomColorPicker(content);
        
        switcher.appendChild(toggle);
        switcher.appendChild(content);
        document.body.appendChild(switcher);
    }
    
    createCustomColorPicker(container) {
        const customSection = document.createElement('div');
        customSection.className = 'custom-theme-section';
        
        const title = document.createElement('h6');
        title.textContent = 'Custom Colors:';
        customSection.appendChild(title);
        
        // Background Color Input
        const bgGroup = this.createColorInput('Background', 'bg-dark', this.customColors.bgDark || '#2b2b2b');
        customSection.appendChild(bgGroup);
        
        // Control Color Input
        const controlGroup = this.createColorInput('Controls', 'control-dark', this.customColors.controlDark || '#3b3b3b');
        customSection.appendChild(controlGroup);
        
        // Primary Color Input
        const primaryGroup = this.createColorInput('Primary', 'primary-color', this.customColors.primaryColor || '#007acc');
        customSection.appendChild(primaryGroup);
        
        // Text Color Input
        const textGroup = this.createColorInput('Text', 'text-light', this.customColors.textLight || '#ffffff');
        customSection.appendChild(textGroup);
        
        // Action buttons
        const actions = document.createElement('div');
        actions.className = 'custom-theme-actions';
        
        const applyBtn = document.createElement('button');
        applyBtn.className = 'custom-theme-btn';
        applyBtn.textContent = 'Apply Custom';
        applyBtn.addEventListener('click', () => this.applyCustomTheme());
        
        const resetBtn = document.createElement('button');
        resetBtn.className = 'custom-theme-btn secondary';
        resetBtn.textContent = 'Reset';
        resetBtn.addEventListener('click', () => this.resetCustomTheme());
        
        actions.appendChild(applyBtn);
        actions.appendChild(resetBtn);
        customSection.appendChild(actions);
        
        container.appendChild(customSection);
    }
    
    createColorInput(label, property, defaultValue) {
        const group = document.createElement('div');
        group.className = 'color-input-group';
        
        const labelEl = document.createElement('label');
        labelEl.textContent = label;
        group.appendChild(labelEl);
        
        const wrapper = document.createElement('div');
        wrapper.className = 'color-input-wrapper';
        
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'color-input';
        input.placeholder = '#2b2b2b';
        input.value = defaultValue;
        input.dataset.property = property;
        
        const preview = document.createElement('input');
        preview.type = 'color';
        preview.className = 'color-preview-input';
        preview.value = defaultValue;
        
        // Sync text input with color picker
        input.addEventListener('input', (e) => {
            const value = e.target.value;
            if (this.isValidHex(value)) {
                preview.value = value;
            }
        });
        
        preview.addEventListener('input', (e) => {
            input.value = e.target.value;
        });
        
        wrapper.appendChild(input);
        wrapper.appendChild(preview);
        group.appendChild(wrapper);
        
        return group;
    }
    
    attachEventListeners() {
        const toggle = document.querySelector('.theme-switcher-toggle');
        const options = document.querySelectorAll('.theme-option');
        
        toggle.addEventListener('click', () => {
            this.toggleSwitcher();
        });
        
        options.forEach(option => {
            option.addEventListener('click', (e) => {
                const themeId = option.dataset.theme;
                this.switchTheme(themeId);
            });
        });
        
        // Close switcher when clicking outside
        document.addEventListener('click', (e) => {
            const switcher = document.querySelector('.theme-switcher');
            if (!switcher.contains(e.target) && !switcher.classList.contains('collapsed')) {
                this.collapseSwitcher();
            }
        });
    }
    
    toggleSwitcher() {
        const switcher = document.querySelector('.theme-switcher');
        this.isCollapsed = !this.isCollapsed;
        
        if (this.isCollapsed) {
            switcher.classList.add('collapsed');
        } else {
            switcher.classList.remove('collapsed');
        }
        
        this.saveCollapsedState();
    }
    
    collapseSwitcher() {
        const switcher = document.querySelector('.theme-switcher');
        switcher.classList.add('collapsed');
        this.isCollapsed = true;
        this.saveCollapsedState();
    }
    
    switchTheme(themeId) {
        if (themeId === this.currentTheme) return;
        
        this.applyTheme(themeId);
        this.updateActiveOption(themeId);
        this.currentTheme = themeId;
        this.saveTheme(themeId);
        
        // Optional: Show a brief success message
        const theme = this.getThemeById(themeId);
        if (theme) {
            this.showThemeChangeNotification(theme.name);
        }
    }
    
    applyTheme(themeId) {
        // Handle custom theme
        if (themeId === 'custom') {
            this.applyCustomColorTheme(this.customColors);
            return;
        }
        
        const theme = this.getThemeById(themeId);
        if (!theme) return;
        
        // Remove custom theme styles
        const customStyle = document.querySelector('#custom-theme-style');
        if (customStyle) {
            customStyle.remove();
        }
        
        // Remove existing theme links
        const existingThemeLinks = document.querySelectorAll('link[href*="theme-"], link[href*="style.css"]');
        existingThemeLinks.forEach(link => {
            if (link.href.includes('base-components.css') || link.href.includes('theme-switcher.css')) {
                return; // Keep base components and switcher styles
            }
            link.remove();
        });
        
        // Add new theme link
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = theme.file;
        document.head.appendChild(link);
    }
    
    updateActiveOption(themeId) {
        const options = document.querySelectorAll('.theme-option');
        options.forEach(option => {
            option.classList.toggle('active', option.dataset.theme === themeId);
        });
    }
    
    getThemeById(themeId) {
        return this.themes.find(theme => theme.id === themeId);
    }
    
    saveTheme(themeId) {
        localStorage.setItem('ozark-finances-theme', themeId);
    }
    
    getSavedTheme() {
        return localStorage.getItem('ozark-finances-theme');
    }
    
    saveCollapsedState() {
        localStorage.setItem('ozark-finances-theme-collapsed', this.isCollapsed.toString());
    }
    
    getSavedCollapsedState() {
        const saved = localStorage.getItem('ozark-finances-theme-collapsed');
        return saved === 'true';
    }
    
    showThemeChangeNotification(themeName) {
        // Remove existing notification if any
        const existing = document.querySelector('.theme-notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--success-color);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            z-index: 1001;
            font-size: 0.9rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            animation: slideDown 0.3s ease;
        `;
        
        notification.innerHTML = `
            <i class="fas fa-check-circle" style="margin-right: 0.5rem;"></i>
            Theme changed to ${themeName}
        `;
        
        // Add animation keyframes if not already present
        if (!document.querySelector('#theme-notification-styles')) {
            const style = document.createElement('style');
            style.id = 'theme-notification-styles';
            style.textContent = `
                @keyframes slideDown {
                    from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
                    to { opacity: 1; transform: translateX(-50%) translateY(0); }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(notification);
        
        // Auto-remove after 2 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideDown 0.3s ease reverse';
                setTimeout(() => notification.remove(), 300);
            }
        }, 2000);
    }
    
    applyCustomTheme() {
        const inputs = document.querySelectorAll('.color-input');
        const customColors = {};
        
        inputs.forEach(input => {
            const property = input.dataset.property;
            const value = input.value;
            
            if (this.isValidHex(value)) {
                customColors[this.camelCase(property)] = value;
            }
        });
        
        // Save custom colors
        this.customColors = customColors;
        this.saveCustomColors(customColors);
        
        // Apply custom theme
        this.applyCustomColorTheme(customColors);
        
        // Update current theme to custom
        this.currentTheme = 'custom';
        this.saveTheme('custom');
        this.updateActiveOption(null); // Clear other active states
        
        this.showThemeChangeNotification('Custom Theme');
    }
    
    applyCustomColorTheme(colors) {
        // Remove existing theme links
        const existingThemeLinks = document.querySelectorAll('link[href*="theme-"], link[href*="style.css"]');
        existingThemeLinks.forEach(link => link.remove());
        
        // Create custom CSS
        const customCSS = this.generateCustomCSS(colors);
        
        // Apply custom styles
        let customStyle = document.querySelector('#custom-theme-style');
        if (!customStyle) {
            customStyle = document.createElement('style');
            customStyle.id = 'custom-theme-style';
            document.head.appendChild(customStyle);
        }
        
        customStyle.textContent = customCSS;
        
        // Also need to load base component styles
        this.loadBaseStyles();
    }
    
    generateCustomCSS(colors) {
        const bgDark = colors.bgDark || '#2b2b2b';
        const controlDark = colors.controlDark || '#3b3b3b';
        const primaryColor = colors.primaryColor || '#007acc';
        const textLight = colors.textLight || '#ffffff';
        
        // Generate complementary colors
        const hoverColor = this.darkenColor(controlDark, 10);
        const primaryHover = this.darkenColor(primaryColor, 15);
        const textMuted = this.lightenColor(textLight, -30);
        const borderColor = this.lightenColor(bgDark, 20);
        
        return `
        :root {
            /* Custom Theme Base Colors */
            --bg-dark: ${bgDark};
            --control-dark: ${controlDark};
            --text-light: ${textLight};
            --text-muted: ${textMuted};
            --border-color: ${borderColor};
            --hover-color: ${hoverColor};
            
            /* Custom Accent Colors */
            --primary-color: ${primaryColor};
            --primary-hover: ${primaryHover};
            --success-color: #38a169;
            --success-light: #68d391;
            --danger-color: #e53e3e;
            --danger-light: #fc8181;
            --warning-color: #d69e2e;
            --info-color: ${primaryColor};
            
            /* Background Variants */
            --bg-light-overlay: ${this.hexToRgba(primaryColor, 0.04)};
            --bg-medium-overlay: ${this.hexToRgba(primaryColor, 0.08)};
            --bg-strong-overlay: ${this.hexToRgba(primaryColor, 0.15)};
            
            /* Border Variants */
            --border-light: ${this.lightenColor(borderColor, 10)};
            --border-medium: ${this.lightenColor(borderColor, 20)};
            --border-strong: ${this.lightenColor(borderColor, 30)};
            
            /* Typography */
            --font-mono: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            --font-size-base: 14px;
        }`;
    }
    
    loadBaseStyles() {
        // Load the base component styles
        if (!document.querySelector('link[href*="base-components.css"]')) {
            const baseLink = document.createElement('link');
            baseLink.rel = 'stylesheet';
            baseLink.href = 'css/base-components.css';
            document.head.appendChild(baseLink);
        }
    }
    
    resetCustomTheme() {
        const inputs = document.querySelectorAll('.color-input');
        const previews = document.querySelectorAll('.color-preview-input');
        
        // Reset to default values
        const defaults = {
            'bg-dark': '#2b2b2b',
            'control-dark': '#3b3b3b',
            'primary-color': '#007acc',
            'text-light': '#ffffff'
        };
        
        inputs.forEach(input => {
            const property = input.dataset.property;
            input.value = defaults[property] || '#2b2b2b';
        });
        
        previews.forEach((preview, index) => {
            const property = inputs[index].dataset.property;
            preview.value = defaults[property] || '#2b2b2b';
        });
    }
    
    saveCustomColors(colors) {
        localStorage.setItem('ozark-finances-custom-colors', JSON.stringify(colors));
    }
    
    getSavedCustomColors() {
        const saved = localStorage.getItem('ozark-finances-custom-colors');
        return saved ? JSON.parse(saved) : {};
    }
    
    isValidHex(hex) {
        return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(hex);
    }
    
    camelCase(str) {
        return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    }
    
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    lightenColor(hex, percent) {
        const num = parseInt(hex.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }
    
    darkenColor(hex, percent) {
        return this.lightenColor(hex, -percent);
    }
}

// Initialize theme switcher when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ThemeSwitcher();
});

// Export for manual initialization if needed
window.ThemeSwitcher = ThemeSwitcher;
