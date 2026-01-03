// Get API URL from current location
const API_URL = window.location.origin;
let authToken = null;
let selectedRating = 0;
let allTools = []; // Store tools data globally for easier access

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadTools();
});

function checkAuth() {
    authToken = localStorage.getItem('authToken');
    if (authToken) {
        document.getElementById('adminBtn').classList.add('hidden');
        document.getElementById('logoutBtn').classList.remove('hidden');
    } else {
        document.getElementById('adminBtn').classList.remove('hidden');
        document.getElementById('logoutBtn').classList.add('hidden');
    }
}

async function loadTools() {
    const category = document.getElementById('categoryFilter').value;
    const pricing = document.getElementById('pricingFilter').value;
    const rating = document.getElementById('ratingFilter').value;

    let url = `${API_URL}/tools?`;
    if (category) url += `category=${category}&`;
    if (pricing) url += `pricing=${pricing}&`;
    if (rating) url += `rating=${rating}&`;

    try {
        const response = await fetch(url);
        const tools = await response.json();
        displayTools(tools);
    } catch (error) {
        console.error('Error loading tools:', error);
    }
}

function displayTools(tools) {
    const grid = document.getElementById('toolsGrid');
    if (tools.length === 0) {
        grid.innerHTML = '<p style="text-align: center; color: #999;">No tools found</p>';
        return;
    }

    grid.innerHTML = tools.map(tool => `
        <div class="tool-card">
            <div class="tool-header">
                <div class="tool-name">${escapeHtml(tool.name)}</div>
                <div class="tool-rating">⭐ ${tool.avg_rating || 'N/A'}</div>
            </div>
            <div>
                <span class="tool-category">${escapeHtml(tool.category)}</span>
                <span class="tool-pricing">${escapeHtml(tool.pricing)}</span>
            </div>
            <div class="tool-description">${escapeHtml(tool.description)}</div>
            <div class="tool-actions">
                <button class="btn btn-success" onclick="showReviewModal(${tool.id})">Write Review</button>
            </div>
        </div>
    `).join('');
}

function showAdminLogin() {
    document.getElementById('loginModal').classList.add('show');
}

async function adminLogin(event) {
    event.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
        const response = await fetch(`${API_URL}/admin/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            showMessage('loginMessage', 'Login successful!', 'success');
            setTimeout(() => {
                closeModal('loginModal');
                checkAuth();
                showAdminPanel();
            }, 1000);
        } else {
            showMessage('loginMessage', 'Invalid credentials', 'error');
        }
    } catch (error) {
        showMessage('loginMessage', 'Login failed', 'error');
    }
}

function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    checkAuth();
    document.getElementById('userSection').classList.remove('hidden');
    document.getElementById('adminSection').classList.add('hidden');
}

function showAdminPanel() {
    document.getElementById('userSection').classList.add('hidden');
    document.getElementById('adminSection').classList.remove('hidden');
    loadAdminTools();
    loadReviews();
}

async function loadAdminTools() {
    try {
        const response = await fetch(`${API_URL}/tools`);
        const tools = await response.json();
        allTools = tools; // Store globally
        displayAdminTools(tools);
    } catch (error) {
        console.error('Error loading admin tools:', error);
    }
}

function displayAdminTools(tools) {
    const grid = document.getElementById('adminToolsGrid');
    grid.innerHTML = tools.map(tool => `
        <div class="tool-card">
            <div class="tool-header">
                <div class="tool-name">${escapeHtml(tool.name)}</div>
                <div class="tool-rating">⭐ ${tool.avg_rating || 'N/A'}</div>
            </div>
            <div>
                <span class="tool-category">${escapeHtml(tool.category)}</span>
                <span class="tool-pricing">${escapeHtml(tool.pricing)}</span>
            </div>
            <div class="tool-description">${escapeHtml(tool.description)}</div>
            <div class="tool-actions">
                <button class="btn btn-primary" onclick="editToolById(${tool.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteTool(${tool.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

async function loadAdminTools() {
    try {
        const response = await fetch(`${API_URL}/tools`);
        const tools = await response.json();
        allTools = tools; // Store globally
        displayAdminTools(tools);
    } catch (error) {
        console.error('Error loading admin tools:', error);
    }
}

function editToolById(toolId) {
    const tool = allTools.find(t => t.id === toolId);
    if (tool) {
        editTool(tool);
    }
}

function showAddToolModal() {
    document.getElementById('toolModalTitle').textContent = 'Add Tool';
    document.getElementById('toolId').value = '';
    document.getElementById('toolName').value = '';
    document.getElementById('toolDescription').value = '';
    document.getElementById('toolUseCase').value = '';
    document.getElementById('toolCategory').value = 'Image Generation';
    document.getElementById('toolPricing').value = 'Free';
    document.getElementById('toolModal').classList.add('show');
}

function editTool(tool) {
    document.getElementById('toolModalTitle').textContent = 'Edit Tool';
    document.getElementById('toolId').value = tool.id;
    document.getElementById('toolName').value = tool.name;
    document.getElementById('toolDescription').value = tool.description;
    document.getElementById('toolUseCase').value = tool.use_case || '';
    document.getElementById('toolCategory').value = tool.category;
    document.getElementById('toolPricing').value = tool.pricing;
    document.getElementById('toolModal').classList.add('show');
}

async function saveTool(event) {
    event.preventDefault();
    const id = document.getElementById('toolId').value;
    const toolData = {
        name: document.getElementById('toolName').value,
        description: document.getElementById('toolDescription').value,
        use_case: document.getElementById('toolUseCase').value,
        category: document.getElementById('toolCategory').value,
        pricing: document.getElementById('toolPricing').value,
        avg_rating: 0
    };

    console.log('Tool ID:', id);
    console.log('Tool Data:', toolData);
    console.log('Auth Token:', authToken);

    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/admin/tools/${id}` : `${API_URL}/admin/tools`;

    console.log('Request URL:', url);
    console.log('Request Method:', method);

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(toolData)
        });

        console.log('Response status:', response.status);
        
        if (response.ok) {
            showMessage('toolMessage', 'Tool saved successfully!', 'success');
            setTimeout(() => {
                closeModal('toolModal');
                loadAdminTools();
                loadTools(); // Refresh user view as well
            }, 1000);
        } else {
            const errorData = await response.json();
            console.error('Error response:', errorData);
            showMessage('toolMessage', `Failed to save tool: ${JSON.stringify(errorData)}`, 'error');
        }
    } catch (error) {
        console.error('Error saving tool:', error);
        showMessage('toolMessage', 'Error saving tool: ' + error.message, 'error');
    }
}

async function deleteTool(id) {
    if (!confirm('Are you sure you want to delete this tool?')) return;

    try {
        const response = await fetch(`${API_URL}/admin/tools/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            loadAdminTools();
            loadTools(); // Refresh user view as well
        }
    } catch (error) {
        alert('Error deleting tool');
    }
}

function showReviewModal(toolId) {
    document.getElementById('reviewToolId').value = toolId;
    document.getElementById('reviewText').value = '';
    selectedRating = 0;
    updateStars();
    document.getElementById('reviewModal').classList.add('show');
}

function setRating(rating) {
    selectedRating = rating;
    document.getElementById('reviewRating').value = rating;
    updateStars();
}

function updateStars() {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < selectedRating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

async function submitReview(event) {
    event.preventDefault();
    const reviewData = {
        tool_id: parseInt(document.getElementById('reviewToolId').value),
        rating: parseFloat(document.getElementById('reviewRating').value),
        review_text: document.getElementById('reviewText').value
    };

    try {
        const response = await fetch(`${API_URL}/review`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reviewData)
        });

        if (response.ok) {
            showMessage('reviewMessage', 'Review submitted successfully!', 'success');
            setTimeout(() => {
                closeModal('reviewModal');
            }, 1500);
        } else {
            showMessage('reviewMessage', 'Failed to submit review', 'error');
        }
    } catch (error) {
        showMessage('reviewMessage', 'Error submitting review', 'error');
    }
}

async function loadReviews() {
    try {
        const response = await fetch(`${API_URL}/admin/reviews`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        const reviews = await response.json();
        displayReviews(reviews);
    } catch (error) {
        console.error('Error loading reviews:', error);
    }
}

function displayReviews(reviews) {
    const list = document.getElementById('reviewsList');
    list.innerHTML = reviews.map(review => `
        <div class="review-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div>
                    <strong>Tool ID: ${review.tool_id}</strong> | Rating: ⭐ ${review.rating}
                </div>
                <span class="review-status ${review.status.toLowerCase()}">${review.status}</span>
            </div>
            <div style="color: #666; margin-bottom: 15px;">${escapeHtml(review.review_text)}</div>
            ${review.status === 'Pending' ? `
                <div style="display: flex; gap: 10px;">
                    <button class="btn btn-success" onclick="approveReview(${review.id})">Approve</button>
                    <button class="btn btn-danger" onclick="rejectReview(${review.id})">Reject</button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function approveReview(id) {
    try {
        const response = await fetch(`${API_URL}/admin/reviews/${id}/approve`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            loadReviews();
            loadAdminTools();
            loadTools(); // Refresh user view as well
        }
    } catch (error) {
        alert('Error approving review');
    }
}

async function rejectReview(id) {
    try {
        const response = await fetch(`${API_URL}/admin/reviews/${id}/reject`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            loadReviews();
        }
    } catch (error) {
        alert('Error rejecting review');
    }
}

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    if (tab === 'tools') {
        document.getElementById('toolsTab').classList.remove('hidden');
        document.getElementById('reviewsTab').classList.add('hidden');
    } else {
        document.getElementById('toolsTab').classList.add('hidden');
        document.getElementById('reviewsTab').classList.remove('hidden');
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="message ${type}">${message}</div>`;
    setTimeout(() => {
        element.innerHTML = '';
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}