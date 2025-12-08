// Pose Detection Test Script
// This script validates the pose detection functionality

console.log('🧪 Starting Pose Detection Tests...');

// Test 1: Check if MediaPipe is available
function testMediaPipeAvailability() {
    try {
        if (typeof Pose !== 'undefined') {
            console.log('✅ MediaPipe Pose is available');
            return true;
        } else {
            console.log('❌ MediaPipe Pose is not available');
            return false;
        }
    } catch (error) {
        console.log('❌ Error checking MediaPipe:', error);
        return false;
    }
}

// Test 2: Check if camera API is available
function testCameraAPI() {
    try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            console.log('✅ Camera API is available');
            return true;
        } else {
            console.log('❌ Camera API is not available');
            return false;
        }
    } catch (error) {
        console.log('❌ Error checking Camera API:', error);
        return false;
    }
}

// Test 3: Check if Web Audio API is available
function testAudioAPI() {
    try {
        if (window.AudioContext || window.webkitAudioContext) {
            console.log('✅ Web Audio API is available');
            return true;
        } else {
            console.log('❌ Web Audio API is not available');
            return false;
        }
    } catch (error) {
        console.log('❌ Error checking Audio API:', error);
        return false;
    }
}

// Test 4: Check if Canvas API is available
function testCanvasAPI() {
    try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (ctx) {
            console.log('✅ Canvas API is available');
            return true;
        } else {
            console.log('❌ Canvas API is not available');
            return false;
        }
    } catch (error) {
        console.log('❌ Error checking Canvas API:', error);
        return false;
    }
}

// Test 5: Check browser permissions
async function testPermissions() {
    try {
        if (navigator.permissions) {
            const result = await navigator.permissions.query({name: 'camera'});
            console.log('✅ Camera permissions can be queried');
            return true;
        } else {
            console.log('⚠️ Camera permissions cannot be queried (older browser)');
            return true; // Still proceed
        }
    } catch (error) {
        console.log('⚠️ Error checking permissions:', error);
        return true; // Still proceed
    }
}

// Test 6: Validate pose detection configuration
function testPoseConfiguration() {
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
        
        console.log('✅ Pose configuration is valid');
        return true;
    } catch (error) {
        console.log('❌ Pose configuration error:', error);
        return false;
    }
}

// Run all tests
async function runAllTests() {
    console.log('🚀 Running comprehensive system tests...\n');
    
    const tests = [
        { name: 'MediaPipe Availability', test: testMediaPipeAvailability },
        { name: 'Camera API', test: testCameraAPI },
        { name: 'Web Audio API', test: testAudioAPI },
        { name: 'Canvas API', test: testCanvasAPI },
        { name: 'Permissions', test: testPermissions },
        { name: 'Pose Configuration', test: testPoseConfiguration }
    ];
    
    let passedTests = 0;
    let totalTests = tests.length;
    
    for (const test of tests) {
        console.log(`\n📋 Testing: ${test.name}`);
        const result = await test.test();
        if (result) passedTests++;
    }
    
    console.log(`\n📊 Test Results: ${passedTests}/${totalTests} tests passed`);
    
    if (passedTests === totalTests) {
        console.log('🎉 All tests passed! The dance game should work perfectly.');
    } else if (passedTests >= totalTests - 1) {
        console.log('✅ Most tests passed. The game should work with minor limitations.');
    } else {
        console.log('⚠️ Some tests failed. The game may not work properly.');
    }
    
    return passedTests === totalTests;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        runAllTests,
        testMediaPipeAvailability,
        testCameraAPI,
        testAudioAPI,
        testCanvasAPI,
        testPermissions,
        testPoseConfiguration
    };
}

// Auto-run tests if in browser
if (typeof window !== 'undefined') {
    window.runAllTests = runAllTests;
    // Run tests after a short delay to allow scripts to load
    setTimeout(runAllTests, 1000);
}