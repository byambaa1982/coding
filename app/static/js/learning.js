// app/static/js/learning.js
// JavaScript for learning interface - video player, progress tracking, and interactions

document.addEventListener('DOMContentLoaded', function() {
    // Video Player Progress Tracking
    const videoElement = document.getElementById('lessonVideo');
    if (videoElement) {
        const lessonId = videoElement.dataset.lessonId;
        const startPosition = parseInt(videoElement.dataset.startPosition) || 0;
        
        // Resume from last position
        if (startPosition > 0) {
            videoElement.currentTime = startPosition;
        }
        
        // Save progress every 5 seconds
        let progressInterval;
        videoElement.addEventListener('play', function() {
            progressInterval = setInterval(() => {
                saveVideoProgress(lessonId, videoElement.currentTime, videoElement.duration);
            }, 5000);
        });
        
        videoElement.addEventListener('pause', function() {
            clearInterval(progressInterval);
            saveVideoProgress(lessonId, videoElement.currentTime, videoElement.duration);
        });
        
        videoElement.addEventListener('ended', function() {
            clearInterval(progressInterval);
            saveVideoProgress(lessonId, videoElement.currentTime, videoElement.duration);
        });
    }
    
    // Mark Lesson as Complete
    const markCompleteBtn = document.getElementById('markCompleteBtn');
    if (markCompleteBtn) {
        markCompleteBtn.addEventListener('click', function() {
            const lessonId = this.dataset.lessonId;
            markLessonComplete(lessonId);
        });
    }
    
    // Toggle Bookmark
    const bookmarkBtn = document.getElementById('bookmarkBtn');
    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', function() {
            const lessonId = this.dataset.lessonId;
            const isBookmarked = this.dataset.bookmarked === 'true';
            toggleBookmark(lessonId, isBookmarked);
        });
    }
    
    // Save Notes
    const saveNotesBtn = document.getElementById('saveNotesBtn');
    const notesTextarea = document.getElementById('lessonNotes');
    if (saveNotesBtn && notesTextarea) {
        saveNotesBtn.addEventListener('click', function() {
            const lessonId = notesTextarea.dataset.lessonId;
            const notes = notesTextarea.value;
            saveNotes(lessonId, notes);
        });
    }
    
    // Video Player Keyboard Shortcuts
    if (videoElement) {
        document.addEventListener('keydown', function(e) {
            // Don't trigger if user is typing in a text field
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            switch(e.key) {
                case ' ':  // Space - Play/Pause
                    e.preventDefault();
                    if (videoElement.paused) {
                        videoElement.play();
                    } else {
                        videoElement.pause();
                    }
                    break;
                    
                case 'ArrowRight':  // Right arrow - Skip forward 10s
                    e.preventDefault();
                    videoElement.currentTime += 10;
                    break;
                    
                case 'ArrowLeft':  // Left arrow - Skip backward 10s
                    e.preventDefault();
                    videoElement.currentTime -= 10;
                    break;
                    
                case 'f':  // F - Fullscreen
                    e.preventDefault();
                    if (videoElement.requestFullscreen) {
                        videoElement.requestFullscreen();
                    } else if (videoElement.webkitRequestFullscreen) {
                        videoElement.webkitRequestFullscreen();
                    }
                    break;
                    
                case 'm':  // M - Mute/Unmute
                    e.preventDefault();
                    videoElement.muted = !videoElement.muted;
                    break;
            }
        });
    }
    
    // Code syntax highlighting (if Prism.js is loaded)
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
    
    // Copy code to clipboard
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'absolute top-2 right-2 px-3 py-1 bg-gray-700 text-white text-sm rounded hover:bg-gray-600';
        copyBtn.textContent = 'Copy';
        copyBtn.addEventListener('click', function() {
            const code = block.textContent;
            navigator.clipboard.writeText(code).then(() => {
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                }, 2000);
            });
        });
        
        const pre = block.parentElement;
        pre.style.position = 'relative';
        pre.appendChild(copyBtn);
    });
});

// Save video progress to server
function saveVideoProgress(lessonId, position, duration) {
    fetch(`/learn/lesson/${lessonId}/update-video-progress`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            position: position,
            duration: duration
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Video progress saved');
        }
    })
    .catch(error => console.error('Error saving video progress:', error));
}

// Mark lesson as complete
function markLessonComplete(lessonId) {
    fetch(`/learn/lesson/${lessonId}/mark-complete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showNotification('Lesson marked as complete! 🎉', 'success');
            
            // Update UI
            const btn = document.getElementById('markCompleteBtn');
            if (btn) {
                btn.outerHTML = `
                    <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                        </svg>
                        Completed
                    </span>
                `;
            }
            
            // Update progress percentage if available
            if (data.progress_percentage !== undefined) {
                const progressBar = document.querySelector('.bg-blue-600.h-2');
                if (progressBar) {
                    progressBar.style.width = `${data.progress_percentage}%`;
                }
            }
        } else {
            showNotification('Error marking lesson as complete', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error marking lesson as complete', 'error');
    });
}

// Toggle bookmark
function toggleBookmark(lessonId, currentlyBookmarked) {
    fetch(`/learn/lesson/${lessonId}/bookmark`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const btn = document.getElementById('bookmarkBtn');
            const svg = btn.querySelector('svg');
            
            if (data.bookmarked) {
                svg.classList.add('fill-yellow-500');
                showNotification('Lesson bookmarked', 'success');
            } else {
                svg.classList.remove('fill-yellow-500');
                showNotification('Bookmark removed', 'success');
            }
            
            btn.dataset.bookmarked = data.bookmarked;
        }
    })
    .catch(error => console.error('Error toggling bookmark:', error));
}

// Save notes
function saveNotes(lessonId, notes) {
    fetch(`/learn/lesson/${lessonId}/notes`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ notes: notes })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Notes saved successfully', 'success');
        } else {
            showNotification('Error saving notes', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error saving notes', 'error');
    });
}

// Get CSRF token from meta tag or cookie
function getCSRFToken() {
    // Try to get from meta tag first
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) {
        return meta.getAttribute('content');
    }
    
    // Fallback to cookie
    const name = 'csrf_token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return '';
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notification if any
    const existing = document.getElementById('notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'notification';
    notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-opacity duration-300 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Quiz timer (if needed)
function startQuizTimer(timeLimit, startTime) {
    const now = Date.now();
    const elapsed = Math.floor((now - startTime) / 1000);
    let remaining = Math.max(0, timeLimit - elapsed);
    
    // Create timer display
    const timerDiv = document.createElement('div');
    timerDiv.id = 'quizTimer';
    timerDiv.className = 'fixed top-4 left-1/2 transform -translate-x-1/2 bg-white shadow-lg rounded-lg px-6 py-3 z-50';
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(timerDiv, container.firstChild);
    }
    
    function updateTimer() {
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;
        
        timerDiv.innerHTML = `
            <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="font-bold ${remaining < 60 ? 'text-red-600' : 'text-gray-800'}">
                    ${minutes}:${seconds.toString().padStart(2, '0')}
                </span>
            </div>
        `;
        
        if (remaining <= 0) {
            clearInterval(timerInterval);
            alert('Time is up! Submitting quiz...');
            document.getElementById('quizForm').submit();
        }
        
        remaining--;
    }
    
    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);
}

// Video playback speed control
function addPlaybackSpeedControl() {
    const videoElement = document.getElementById('lessonVideo');
    if (!videoElement) return;
    
    const speeds = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];
    const currentSpeed = 1;
    
    const speedControl = document.createElement('div');
    speedControl.className = 'absolute bottom-16 right-4 bg-white shadow-lg rounded-lg p-2';
    speedControl.innerHTML = `
        <select id="playbackSpeed" class="px-3 py-1 border border-gray-300 rounded">
            ${speeds.map(speed => `
                <option value="${speed}" ${speed === currentSpeed ? 'selected' : ''}>
                    ${speed}x
                </option>
            `).join('')}
        </select>
    `;
    
    const videoContainer = videoElement.parentElement;
    videoContainer.style.position = 'relative';
    videoContainer.appendChild(speedControl);
    
    document.getElementById('playbackSpeed').addEventListener('change', function() {
        videoElement.playbackRate = parseFloat(this.value);
    });
}
