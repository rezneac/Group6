// script.js

// Highlight active link in navbar
const navLinks = document.querySelectorAll('.nav-links li a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navLinks.forEach(nav => nav.classList.remove('active'));
        link.classList.add('active');
    });
});

// Scroll-to-Top Button
const scrollToTopBtn = document.createElement('button');
scrollToTopBtn.textContent = "↑";
scrollToTopBtn.classList.add('scroll-to-top');
document.body.appendChild(scrollToTopBtn);

scrollToTopBtn.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    padding: 0.5rem 1rem;
    background: #ff7b54;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    display: none;
    z-index: 1000;
`;

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        scrollToTopBtn.style.display = 'block';
    } else {
        scrollToTopBtn.style.display = 'none';
    }
});

scrollToTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Receipt Upload Preview
const receiptInput = document.querySelector('#receipt-upload');
const receiptPreview = document.querySelector('#receipt-preview');

if (receiptInput && receiptPreview) {
    receiptInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                receiptPreview.src = e.target.result;
                receiptPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
}

// FAQ Accordion
// Toggle FAQ answers
const faqItems = document.querySelectorAll('.faq-item');

faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    question.addEventListener('click', () => {
        // Close all open FAQs
        faqItems.forEach(faq => {
            if (faq !== item) faq.classList.remove('active');
            const answer = faq.querySelector('.faq-answer');
            answer.style.maxHeight = faq.classList.contains('active') ? answer.scrollHeight + 'px' : '0';
        });

        // Toggle current FAQ
        item.classList.toggle('active');
        const answer = item.querySelector('.faq-answer');
        answer.style.maxHeight = item.classList.contains('active') ? answer.scrollHeight + 'px' : '0';
    });
});

// Generate a consistent color for each user
function getUserColor(username) {
    let hash = 0;
    for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash);
    }
    const color = `hsl(${hash % 360}, 70%, 50%)`; // Unique color based on username
    return color;
}

// Fetch savings data from the Flask backend
async function fetchSavingsData() {
    try {
        const response = await fetch('/savings');
        const savingsData = await response.json();
        displaySavingsProgress(savingsData);
    } catch (error) {
        console.error('Error fetching savings data:', error);
    }
}

// Display savings progress for individual users and overall progress
function displaySavingsProgress(savingsData) {
    const usersContainer = document.getElementById('users-container');
    const globalProgressContainer = document.getElementById('global-progress-container');
    
    usersContainer.innerHTML = '';  // Clear previous content
    globalProgressContainer.innerHTML = '';

    let totalGoal = savingsData["goal"]["target_amount"]
    let totalSaved = savingsData["users"].reduce((sum, user) => sum + user.saved_amount, 0);

    // Global stacked progress bar (total savings)
    if (totalSaved > 0) {
        savingsData["users"].forEach(user => {
            if (user.saved_amount > 0) {
                const progressSegment = document.createElement('div');
                progressSegment.classList.add('progress-bar');
                progressSegment.style.width = `${(user.saved_amount / totalGoal) * 100}%`;
                progressSegment.style.backgroundColor = getUserColor(user.username);
                progressSegment.textContent = `£${user.saved_amount}`;
                globalProgressContainer.appendChild(progressSegment);
            }
        });
    } else {
        globalProgressContainer.textContent = "No savings yet.";
    }

    document.getElementById("global-progress-goal").textContent = savingsData["goal"]["name"];

    // Individual user progress bars
    savingsData["users"].forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.classList.add('user-progress');

        const usernameDiv = document.createElement('div');
        usernameDiv.classList.add('username');
        usernameDiv.textContent = `${user.username} - Goal: £${totalGoal}, Saved: £${user.saved_amount}`;

        const progressAndGoalContainer = document.createElement('div');
        progressAndGoalContainer.classList.add('progress-and-goal-container');

        const progressContainer = document.createElement('div');
        progressContainer.classList.add('progress-container');

        const goalText = document.createElement('div');
        goalText.textContent = savingsData["goal"]["name"];
        goalText.classList.add("progress-goal");

        if (user.saved_amount > 0) {
            console.table(user.contributions);
            user.contributions.forEach(contrib => {
                const progressBar = document.createElement('div');
                progressBar.classList.add('progress-bar');
                progressBar.style.width = `${(contrib.amount / totalGoal) * 100}%`;
                progressBar.style.backgroundColor = getUserColor(contrib.username);
                progressBar.textContent = `£${contrib.amount}`;
                progressContainer.appendChild(progressBar);
            });
        } else {
            progressContainer.textContent = "No savings yet.";
        }

        progressAndGoalContainer.appendChild(progressContainer);
        progressAndGoalContainer.appendChild(goalText);


        userDiv.appendChild(usernameDiv);
        userDiv.appendChild(progressAndGoalContainer);
        usersContainer.appendChild(userDiv);
    });
}

// Fetch savings data when the page loads
fetchSavingsData();
