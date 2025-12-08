# Cyber Rhythm Dance Game

A full-body motion rhythm dance game that uses camera-based pose detection to track your movements and sync them with music beats. No keyboard or mouse input required - just dance!

## Features

- **Camera-based Pose Detection**: Real-time body tracking using MediaPipe
- **Music Rhythm Sync**: Beat-synchronized gameplay with generated electronic music
- **Timed Move Prompts**: Visual prompts showing upcoming dance moves
- **Score Calculation**: Points based on pose accuracy and timing
- **Particle Effects**: Visual feedback with animated particle systems
- **Cyberpunk Aesthetic**: Dark mode with neon colors and glassmorphism design
- **Motion-Controlled**: Pure gesture-based interaction during gameplay

## How to Play

1. **Start the Game**: Click "START DANCING" on the start screen
2. **Allow Camera Access**: Grant camera permissions when prompted
3. **Follow the Beat**: Watch the right-side timeline for upcoming moves
4. **Hit the Target**: When poses reach the center circle, perform the move
5. **Get Scored**: Perfect timing and accurate poses earn more points

## Dance Moves

- **ARMS UP**: Raise both arms above your head
- **LEFT/RIGHT**: Extend left or right arm to the side
- **JUMP**: Jump with arms raised
- **TURN**: Turn your head/body around
- **CLAP**: Bring both hands together
- **DANCE**: Free-form movement with energy

## Technical Implementation

### Core Technologies
- **MediaPipe Pose**: Real-time pose detection and tracking
- **Web Audio API**: Music generation and beat synchronization
- **Canvas API**: Real-time graphics and particle effects
- **CSS3**: Modern glassmorphism UI design

### Key Features
- **Pose Smoothing**: Multiple frame averaging for stable detection
- **Beat Detection**: 120 BPM rhythm with precise timing windows
- **Adaptive Scoring**: Tolerance-based pose matching algorithm
- **Responsive Design**: Works on desktop and tablet devices

### Performance Optimizations
- Efficient pose history management (500ms window)
- Optimized particle system with automatic cleanup
- Smooth CSS animations for UI feedback
- Progressive loading of MediaPipe models

## Browser Compatibility

- **Chrome**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support (requires camera permissions)
- **Mobile**: Limited (tablet portrait mode recommended)

## Setup Instructions

1. **Open the Game**: Open `index.html` in a modern web browser
2. **Camera Permissions**: Allow camera access when prompted
3. **Internet Connection**: Required for MediaPipe model loading
4. **Audio Setup**: Audio will start automatically after countdown

## Game Controls

- **No controls during gameplay** - purely motion-controlled
- **Start/Restart**: Button on start screen or alert dialog

## Scoring System

- **Perfect**: 100 points (accurate pose + perfect timing)
- **Good**: 50 points (acceptable pose + good timing)
- **Miss**: 0 points (missed timing window)

## Tips for Better Performance

1. **Good Lighting**: Ensure adequate lighting for pose detection
2. **Clear Space**: Have enough room to move freely
3. **Face the Camera**: Stay in frame for optimal tracking
4. **Clear Movements**: Make exaggerated, clear gestures
5. **Stay Centered**: Position yourself in the middle of the camera view

## File Structure

```
/
├── index.html          # Main game interface
├── dance-game.js       # Core game logic and pose detection
└── README.md          # This documentation
```

## Troubleshooting

**Camera Not Working**: Check browser permissions and ensure HTTPS connection

**Slow Performance**: Close other browser tabs and ensure good lighting

**Pose Detection Issues**: Stand farther back to fit more of your body in frame

**Audio Issues**: Ensure browser allows audio autoplay and check volume

## Future Enhancements

- Multiple difficulty levels
- Custom music upload
- Multiplayer mode
- More complex pose recognition
- Performance analytics
- Social sharing features

---

**Note**: This game requires camera access and an internet connection to load the pose detection models. Make sure you're in a well-lit environment with enough space to dance safely.