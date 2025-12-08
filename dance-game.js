class DanceGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.cameraFeed = document.getElementById('cameraFeed');
        this.scoreElement = document.getElementById('score');
        this.progressFill = document.getElementById('progressFill');
        this.feedbackText = document.getElementById('feedbackText');
        this.countdown = document.getElementById('countdown');
        
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        
        this.score = 0;
        this.gameState = 'start'; // start, countdown, playing, gameover
        this.currentBeat = 0;
        this.poseSequence = [];
        this.activePose = null;
        this.poseTiming = [];
        
        // Audio context and analyser
        this.audioContext = null;
        this.audioAnalyser = null;
        this.songBuffer = null;
        this.songSource = null;
        this.startTime = null;
        this.songDuration = 120; // 2 minutes
        
        // Pose detection
        this.pose = null;
        this.poseDetector = null;
        this.currentPose = null;
        this.poseHistory = [];
        
        // Game timing
        this.bpm = 120;
        this.beatInterval = 60000 / this.bpm; // milliseconds per beat
        this.lastBeatTime = 0;
        
        // Particle system
        this.particles = [];
        
        // Initialize
        this.initPoseDetection();
        this.generatePoseSequence();
        this.setupEventListeners();
    }
    
    async initPoseDetection() {
        try {
            const pose = new Pose.Pose({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/${file}`;
                }
            });
            
            pose.setOptions({
                modelComplexity: 1,
                smoothLandmarks: true,
                enableSegmentation: false,
                smoothSegmentation: false,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });
            
            pose.onResults((results) => {
                this.currentPose = results.poseLandmarks;
            });
            
            const camera = new Camera(this.cameraFeed, {
                onFrame: async () => {
                    await pose.send({ image: this.cameraFeed });
                },
                width: 640,
                height: 480
            });
            
            this.pose = pose;
            this.camera = camera;
            
        } catch (error) {
            console.error('Failed to initialize pose detection:', error);
        }
    }
    
    generatePoseSequence() {
        // Generate a sequence of dance moves
        const poses = [
            { name: 'ARMS UP', target: 'arms_up', description: 'Raise both arms' },
            { name: 'LEFT', target: 'left_arm', description: 'Left arm to side' },
            { name: 'RIGHT', target: 'right_arm', description: 'Right arm to side' },
            { name: 'JUMP', target: 'jump', description: 'Jump with arms up' },
            { name: 'TURN', target: 'turn', description: 'Turn around' },
            { name: 'CLAP', target: 'clap', description: 'Clap hands' },
            { name: 'DANCE', target: 'dance', description: 'Free dance' }
        ];
        
        const sequenceLength = 32; // Number of poses in sequence
        const beatsBetweenPoses = 2; // Each pose lasts 2 beats (4 seconds at 120 BPM)
        
        for (let i = 0; i < sequenceLength; i++) {
            const poseIndex = Math.floor(i / beatsBetweenPoses) % poses.length;
            const pose = poses[poseIndex];
            const beatTime = i * (this.beatInterval * beatsBetweenPoses);
            
            this.poseSequence.push({
                ...pose,
                beatTime: beatTime,
                completed: false,
                position: 0 // 0 to 1, for animation
            });
        }
    }
    
    setupEventListeners() {
        window.addEventListener('resize', () => {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        });
    }
    
    async startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 },
                audio: false
            });
            this.cameraFeed.srcObject = stream;
            this.camera.start();
        } catch (error) {
            console.error('Failed to access camera:', error);
            alert('Camera access is required for this game. Please allow camera permissions.');
        }
    }
    
    async startAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Create a simple beat track programmatically
            const sampleRate = this.audioContext.sampleRate;
            const duration = this.songDuration;
            const buffer = this.audioContext.createBuffer(2, duration * sampleRate, sampleRate);
            
            // Generate a simple electronic beat
            for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
                const channelData = buffer.getChannelData(channel);
                
                for (let i = 0; i < channelData.length; i++) {
                    const time = i / sampleRate;
                    const beatPos = (time * this.bpm / 60) % 1;
                    
                    // Kick drum on beat
                    if (beatPos < 0.1) {
                        channelData[i] = Math.sin(2 * Math.PI * 60 * time) * Math.exp(-time * 10) * 0.3;
                    }
                    // Hi-hat
                    else if (beatPos < 0.3) {
                        channelData[i] = (Math.random() - 0.5) * 0.1 * Math.exp(-time * 20);
                    }
                    // Melody
                    else {
                        const melodyFreq = 220 + Math.sin(time * 2) * 50;
                        channelData[i] = Math.sin(2 * Math.PI * melodyFreq * time) * 0.05;
                    }
                }
            }
            
            this.songBuffer = buffer;
            
        } catch (error) {
            console.error('Failed to initialize audio:', error);
        }
    }
    
    startGame() {
        this.gameState = 'countdown';
        this.score = 0;
        this.updateScore();
        
        // Start countdown
        this.showCountdown();
        
        // Start camera and audio after countdown
        setTimeout(() => {
            this.startCamera();
            this.startAudio();
            
            setTimeout(() => {
                this.startGameplay();
            }, 1000);
        }, 3000);
    }
    
    showCountdown() {
        const numbers = ['3', '2', '1', 'GO!'];
        let index = 0;
        
        const showNumber = () => {
            if (index < numbers.length) {
                this.countdown.textContent = numbers[index];
                this.countdown.classList.add('show');
                
                setTimeout(() => {
                    this.countdown.classList.remove('show');
                    index++;
                    setTimeout(showNumber, 200);
                }, 800);
            }
        };
        
        showNumber();
    }
    
    startGameplay() {
        this.gameState = 'playing';
        this.startTime = Date.now();
        this.lastBeatTime = this.startTime;
        
        // Start audio playback
        if (this.audioContext && this.songBuffer) {
            this.songSource = this.audioContext.createBufferSource();
            this.songSource.buffer = this.songBuffer;
            this.songSource.connect(this.audioContext.destination);
            this.songSource.start();
        }
        
        // Start game loop
        this.gameLoop();
    }
    
    gameLoop() {
        if (this.gameState !== 'playing') return;
        
        const currentTime = Date.now();
        const elapsed = currentTime - this.startTime;
        
        // Update progress
        const progress = (elapsed / (this.songDuration * 1000)) * 100;
        this.progressFill.style.width = `${Math.min(progress, 100)}%`;
        
        // Check for active poses
        this.updateActivePoses(elapsed);
        
        // Detect current pose
        this.detectCurrentPose();
        
        // Update particle system
        this.updateParticles();
        
        // Clear and redraw canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.renderPoseTimeline();
        this.renderParticles();
        
        // Check game end
        if (elapsed >= this.songDuration * 1000) {
            this.endGame();
            return;
        }
        
        requestAnimationFrame(() => this.gameLoop());
    }
    
    updateActivePoses(currentTime) {
        const poseTimeline = document.querySelector('.pose-timeline');
        
        // Update pose positions
        this.poseSequence.forEach((pose, index) => {
            const timeDiff = currentTime - pose.beatTime;
            const progress = timeDiff / (this.beatInterval * 4); // 4 beats per pose window
            
            if (progress >= 0 && progress <= 1 && !pose.completed) {
                // Pose is in the active window
                const poseElement = document.querySelector(`[data-pose-index="${index}"]`);
                if (poseElement) {
                    poseElement.style.opacity = '1';
                    
                    // Pulsing effect when in hit zone
                    if (progress >= 0.4 && progress <= 0.6) {
                        poseElement.style.boxShadow = '0 0 20px #99f6e4';
                        poseElement.style.borderColor = '#99f6e4';
                    } else {
                        poseElement.style.boxShadow = 'none';
                        poseElement.style.borderColor = '#2DD4BF';
                    }
                }
                
                // Check for successful pose completion
                if (this.checkPoseCompletion(pose)) {
                    this.completePose(pose, index);
                }
            } else if (progress > 1 && !pose.completed) {
                // Pose window missed
                this.missPose(pose, index);
            }
        });
        
        // Update pose timeline if it doesn't exist
        if (!document.querySelector(`[data-pose-index="0"]`)) {
            this.renderPoseTimeline();
        }
    }
    
    renderPoseTimeline() {
        const poseTimeline = document.querySelector('.pose-timeline');
        
        // Clear existing poses
        document.querySelectorAll('.pose-prompt').forEach(el => el.remove());
        
        // Render upcoming poses
        this.poseSequence.forEach((pose, index) => {
            const timeDiff = Date.now() - this.startTime - pose.beatTime;
            const progress = timeDiff / (this.beatInterval * 4);
            
            if (progress >= -1 && progress <= 2) { // Show poses slightly before and after
                const poseElement = document.createElement('div');
                poseElement.className = 'pose-prompt';
                poseElement.dataset.poseIndex = index;
                poseElement.textContent = pose.name;
                
                // Position based on time progress
                const position = Math.max(0, Math.min(1, (progress + 1) / 3));
                poseElement.style.top = `${(1 - position) * 300}px`;
                poseElement.style.left = '50%';
                poseElement.style.transform = 'translateX(-50%)';
                
                poseTimeline.appendChild(poseElement);
            }
        });
    }
    
    detectCurrentPose() {
        if (!this.currentPose) return;
        
        // Store pose history for smoothing
        this.poseHistory.push({
            timestamp: Date.now(),
            pose: this.currentPose
        });
        
        // Keep only recent poses (last 500ms)
        this.poseHistory = this.poseHistory.filter(p => 
            Date.now() - p.timestamp < 500
        );
    }
    
    checkPoseCompletion(pose) {
        if (this.poseHistory.length < 3) return false; // Need multiple samples
        
        // Get average pose from recent history
        const recentPoses = this.poseHistory.slice(-3);
        const avgPose = this.averagePose(recentPoses);
        
        return this.comparePoseToTarget(avgPose, pose);
    }
    
    averagePose(poses) {
        if (poses.length === 0) return null;
        
        const result = [];
        for (let i = 0; i < poses[0].pose.length; i++) {
            let sumX = 0, sumY = 0;
            for (let pose of poses) {
                sumX += pose.pose[i].x;
                sumY += pose.pose[i].y;
            }
            result.push({
                x: sumX / poses.length,
                y: sumY / poses.length
            });
        }
        return result;
    }
    
    comparePoseToTarget(pose, target) {
        if (!pose) return false;
        
        const tolerance = 0.15; // 15% tolerance for pose matching
        
        switch (target.target) {
            case 'arms_up':
                return this.checkArmsUp(pose, tolerance);
            case 'left_arm':
                return this.checkLeftArm(pose, tolerance);
            case 'right_arm':
                return this.checkRightArm(pose, tolerance);
            case 'jump':
                return this.checkJump(pose, tolerance);
            case 'turn':
                return this.checkTurn(pose, tolerance);
            case 'clap':
                return this.checkClap(pose, tolerance);
            case 'dance':
                return this.checkDance(pose, tolerance);
            default:
                return false;
        }
    }
    
    checkArmsUp(pose, tolerance) {
        const leftWrist = pose[15]; // Left wrist
        const rightWrist = pose[16]; // Right wrist
        const leftShoulder = pose[11]; // Left shoulder
        const rightShoulder = pose[12]; // Right shoulder
        
        return leftWrist.y < leftShoulder.y - tolerance && 
               rightWrist.y < rightShoulder.y - tolerance;
    }
    
    checkLeftArm(pose, tolerance) {
        const leftWrist = pose[15];
        const leftShoulder = pose[11];
        
        return leftWrist.x < leftShoulder.x - tolerance;
    }
    
    checkRightArm(pose, tolerance) {
        const rightWrist = pose[16];
        const rightShoulder = pose[12];
        
        return rightWrist.x > rightShoulder.x + tolerance;
    }
    
    checkJump(pose, tolerance) {
        const leftHip = pose[23];
        const rightHip = pose[24];
        const leftAnkle = pose[27];
        const rightAnkle = pose[28];
        
        // Check if ankles are significantly below hips (indicating a jump)
        return (leftAnkle.y < leftHip.y - tolerance * 2) && 
               (rightAnkle.y < rightHip.y - tolerance * 2);
    }
    
    checkTurn(pose, tolerance) {
        const nose = pose[0];
        const leftShoulder = pose[11];
        const rightShoulder = pose[12];
        
        const shoulderCenterX = (leftShoulder.x + rightShoulder.x) / 2;
        const turnAngle = Math.atan2(nose.x - shoulderCenterX, nose.y - leftShoulder.y);
        
        return Math.abs(turnAngle) > tolerance * 3; // Significant head turn
    }
    
    checkClap(pose, tolerance) {
        const leftWrist = pose[15];
        const rightWrist = pose[16];
        
        const distance = Math.sqrt(
            Math.pow(leftWrist.x - rightWrist.x, 2) + 
            Math.pow(leftWrist.y - rightWrist.y, 2)
        );
        
        return distance < tolerance * 2; // Wrists close together
    }
    
    checkDance(pose, tolerance) {
        // For free dance, we look for general movement and energy
        if (this.poseHistory.length < 5) return false;
        
        // Check for overall movement and variance in pose
        let totalMovement = 0;
        for (let i = 1; i < this.poseHistory.length; i++) {
            const prevPose = this.poseHistory[i-1].pose;
            const currPose = this.poseHistory[i].pose;
            
            for (let j = 0; j < Math.min(prevPose.length, currPose.length); j += 2) {
                const movement = Math.sqrt(
                    Math.pow(prevPose[j].x - currPose[j].x, 2) + 
                    Math.pow(prevPose[j+1].y - currPose[j+1].y, 2)
                );
                totalMovement += movement;
            }
        }
        
        return totalMovement / this.poseHistory.length > tolerance;
    }
    
    completePose(pose, index) {
        pose.completed = true;
        this.score += 100;
        this.updateScore();
        this.showFeedback('PERFECT!', 'success');
        this.createParticles('success');
    }
    
    missPose(pose, index) {
        pose.completed = true;
        this.showFeedback('MISS', 'error');
        this.createParticles('error');
    }
    
    updateScore() {
        this.scoreElement.textContent = this.score.toLocaleString();
    }
    
    showFeedback(text, type) {
        const colors = {
            success: '#34D399',
            warning: '#FBBF24',
            error: '#F87171'
        };
        
        this.feedbackText.textContent = text;
        this.feedbackText.style.color = colors[type] || colors.success;
        this.feedbackText.classList.add('show');
        
        setTimeout(() => {
            this.feedbackText.classList.remove('show');
        }, 600);
    }
    
    createParticles(type) {
        const colors = {
            success: ['#34D399', '#2DD4BF', '#99f6e4'],
            error: ['#F87171', '#EF4444'],
            warning: ['#FBBF24', '#F59E0B']
        };
        
        const particleCount = type === 'success' ? 15 : 8;
        const particleColors = colors[type] || colors.success;
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: window.innerWidth / 2 + (Math.random() - 0.5) * 100,
                y: window.innerHeight / 2 + (Math.random() - 0.5) * 100,
                vx: (Math.random() - 0.5) * 8,
                vy: (Math.random() - 0.5) * 8,
                life: 1,
                decay: 0.02,
                color: particleColors[Math.floor(Math.random() * particleColors.length)],
                size: Math.random() * 4 + 2
            });
        }
    }
    
    updateParticles() {
        this.particles = this.particles.filter(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.vy += 0.2; // Gravity
            particle.life -= particle.decay;
            
            return particle.life > 0;
        });
    }
    
    renderParticles() {
        this.particles.forEach(particle => {
            this.ctx.save();
            this.ctx.globalAlpha = particle.life;
            this.ctx.fillStyle = particle.color;
            this.ctx.shadowBlur = 10;
            this.ctx.shadowColor = particle.color;
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
        });
    }
    
    endGame() {
        this.gameState = 'gameover';
        
        // Stop audio
        if (this.songSource) {
            this.songSource.stop();
        }
        
        // Show final score
        setTimeout(() => {
            alert(`Game Over! Final Score: ${this.score.toLocaleString()}`);
            this.resetGame();
        }, 1000);
    }
    
    resetGame() {
        this.gameState = 'start';
        this.score = 0;
        this.poseSequence = [];
        this.poseHistory = [];
        this.particles = [];
        this.currentPose = null;
        
        this.generatePoseSequence();
        this.updateScore();
        this.progressFill.style.width = '0%';
        
        // Show start screen
        document.getElementById('startScreen').style.display = 'flex';
    }
}

// Global game instance
let game;

// Initialize game when page loads
window.addEventListener('DOMContentLoaded', () => {
    game = new DanceGame();
});

// Start game function
function startGame() {
    document.getElementById('startScreen').style.display = 'none';
    game.startGame();
}