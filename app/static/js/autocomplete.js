const input = document.querySelector('.search-input');
const form = document.querySelector('.search-form');

// Create dropdown
const dropdown = document.createElement('div');
dropdown.classList.add('autocomplete-dropdown');
dropdown.style.display = 'none';
input.parentNode.style.position = 'relative';
input.parentNode.insertBefore(dropdown, input.nextSibling);

let debounceTimer;
let selectedIndex = -1;

input.addEventListener('input', () => {
    const query = input.value.trim();
    clearTimeout(debounceTimer);
    selectedIndex = -1;

    if (query.length < 3) {
        hideDropdown();
        return;
    }

    // Debounce — wait 300ms after user stops typing before calling API
    debounceTimer = setTimeout(() => fetchSuggestions(query), 300);
});

async function fetchSuggestions(query) {
    try {
        const response = await fetch(`/suggest?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        renderDropdown(data.suggestions);
    } catch (err) {
        hideDropdown();
    }
}

function renderDropdown(suggestions) {
    dropdown.innerHTML = '';

    if (suggestions.length === 0) {
        hideDropdown();
        return;
    }

    suggestions.forEach((suggestion, index) => {
        const item = document.createElement('div');
        item.classList.add('autocomplete-item');
        item.textContent = suggestion.label;
        item.dataset.value = suggestion.value;

        item.addEventListener('mousedown', (e) => {
            e.preventDefault();
            selectSuggestion(suggestion);
        });

        item.addEventListener('mouseover', () => {
            setActive(index);
        });

        dropdown.appendChild(item);
    });

    dropdown.style.display = 'block';
}

function selectSuggestion(suggestion) {
    if (suggestion.lat && suggestion.lon) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/weather-by-coords';

        const fields = {
            lat: suggestion.lat,
            lon: suggestion.lon,
            state: suggestion.state || ''
        };

        Object.entries(fields).forEach(([name, value]) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            input.value = value;
            form.appendChild(input);
        });

        document.body.appendChild(form);
        form.submit();
    } else {
        input.value = suggestion.value;
        hideDropdown();
        document.querySelector('.search-form').submit();
    }
}
function setActive(index) {
    const items = dropdown.querySelectorAll('.autocomplete-item');
    items.forEach(i => i.classList.remove('active'));
    if (index >= 0 && index < items.length) {
        items[index].classList.add('active');
        selectedIndex = index;
    }
}

// Keyboard navigation
input.addEventListener('keydown', (e) => {
    const items = dropdown.querySelectorAll('.autocomplete-item');
    if (!items.length) return;

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        setActive(Math.min(selectedIndex + 1, items.length - 1));
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setActive(Math.max(selectedIndex - 1, 0));
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
        e.preventDefault();
        const selected = items[selectedIndex];
        input.value = selected.dataset.value;
        hideDropdown();
        form.submit();
    } else if (e.key === 'Escape') {
        hideDropdown();
    }
});

document.addEventListener('click', (e) => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        hideDropdown();
    }
});

function hideDropdown() {
    dropdown.style.display = 'none';
    selectedIndex = -1;
}