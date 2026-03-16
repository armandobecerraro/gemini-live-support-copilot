import { renderHook, act } from '@testing-library/react';
import { useAudioRecorder } from '../src/hooks/useAudioRecorder';
import { useScreenCapture } from '../src/hooks/useScreenCapture';

describe('useAudioRecorder', () => {
  const mockStart = jest.fn();
  const mockStop = jest.fn();

  beforeEach(() => {
    (window as any).webkitSpeechRecognition = jest.fn().mockImplementation(() => ({
      start: mockStart,
      stop: mockStop,
      continuous: false,
      interimResults: false,
      lang: '',
      onresult: null,
    }));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('starts and stops recording', () => {
    const { result } = renderHook(() => useAudioRecorder());

    act(() => {
      result.current.startRecording();
    });

    expect(result.current.isRecording).toBe(true);
    expect(mockStart).toHaveBeenCalled();

    act(() => {
      result.current.stopRecording();
    });

    expect(result.current.isRecording).toBe(false);
    expect(mockStop).toHaveBeenCalled();
  });

  it('clears transcript', () => {
    const { result } = renderHook(() => useAudioRecorder());
    
    act(() => {
      result.current.clearTranscript();
    });
    expect(result.current.transcript).toBe('');
  });

  it('handles speech recognition result', () => {
    let resultCallback: any;
    (window as any).webkitSpeechRecognition = jest.fn().mockImplementation(() => ({
      start: mockStart,
      stop: mockStop,
      set onresult(cb: any) { resultCallback = cb; },
      get onresult() { return resultCallback; }
    }));

    const { result } = renderHook(() => useAudioRecorder());

    act(() => {
      result.current.startRecording();
    });

    const mockEvent = {
      resultIndex: 0,
      results: [
        {
          isFinal: true,
          0: { transcript: 'hello world' },
          length: 1
        }
      ]
    };

    act(() => {
      resultCallback(mockEvent);
    });

    expect(result.current.transcript).toContain('hello world');
  });

  it('handles speech recognition not supported', () => {
    const originalSR = window.SpeechRecognition;
    const originalWSR = window.webkitSpeechRecognition;
    delete (window as any).SpeechRecognition;
    delete (window as any).webkitSpeechRecognition;
    
    const alertSpy = jest.spyOn(window, 'alert').mockImplementation();
    const { result } = renderHook(() => useAudioRecorder());
    
    act(() => {
      result.current.startRecording();
    });
    
    expect(alertSpy).toHaveBeenCalledWith('Speech recognition not supported in this browser.');
    expect(result.current.isRecording).toBe(false);
    
    (window as any).SpeechRecognition = originalSR;
    (window as any).webkitSpeechRecognition = originalWSR;
    alertSpy.mockRestore();
  });
});

describe('useScreenCapture', () => {
  const mockStop = jest.fn();
  const mockGetDisplayMedia = jest.fn().mockResolvedValue({
    getVideoTracks: () => [{ stop: mockStop }],
  });

  beforeEach(() => {
    (navigator as any).mediaDevices = {
      getDisplayMedia: mockGetDisplayMedia,
    };
    (window as any).ImageCapture = jest.fn().mockImplementation(() => ({
      grabFrame: jest.fn().mockResolvedValue({ width: 100, height: 100 }),
    }));
    // Mock canvas context
    const mockContext = {
      drawImage: jest.fn(),
    };
    jest.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
      if (tagName === 'canvas') {
        return {
          getContext: () => mockContext,
          toDataURL: () => 'data:image/png;base64,mockdata',
          width: 0,
          height: 0,
        } as any;
      }
      return originalCreateElement(tagName);
    });
  });

  const originalCreateElement = document.createElement.bind(document);

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('captures screen', async () => {
    const { result } = renderHook(() => useScreenCapture());

    await act(async () => {
      await result.current.captureScreen();
    });

    expect(mockGetDisplayMedia).toHaveBeenCalled();
    expect(result.current.capturedImage).toBe('mockdata');
    expect(mockStop).toHaveBeenCalled();
  });

  it('clears capture', () => {
    const { result } = renderHook(() => useScreenCapture());
    act(() => {
      result.current.clearCapture();
    });
    expect(result.current.capturedImage).toBeNull();
  });

  it('handles capture error', async () => {
    (navigator as any).mediaDevices.getDisplayMedia = jest.fn().mockRejectedValue(new Error('Permission denied'));
    const { result } = renderHook(() => useScreenCapture());
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    await act(async () => {
      await result.current.captureScreen();
    });

    expect(consoleSpy).toHaveBeenCalledWith('Screen capture failed:', expect.anything());
    expect(result.current.capturedImage).toBeNull();
    consoleSpy.mockRestore();
  });
});
