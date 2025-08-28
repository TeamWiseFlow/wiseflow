// 增强的反检测脚本 - Enhanced Navigator Overrider
(() => {
    'use strict';

    // 通用函数：让函数看起来像原生函数
    const nativeToStringFunctionString = Error.toString().replace(/Error/g, "toString");
    const likeNative = (fn, fnStr) => {
        const handler = {
            apply: function (target, thisArg, args) {
                return target.apply(thisArg, args);
            },
            get: function (target, prop) {
                if (prop === 'toString') {
                    return () => fnStr || nativeToStringFunctionString;
                }
                return Reflect.get(target, prop);
            }
        };
        return new Proxy(fn, handler);
    };

    // 1. 隐藏 webdriver 属性
    Object.defineProperty(navigator, 'webdriver', {
        get: likeNative(() => undefined, nativeToStringFunctionString),
        configurable: true
    });

    // 删除 webdriver 从原型链
    delete navigator.__proto__.webdriver;

    // 2. 伪造 Chrome 对象
    if (!window.navigator.chrome) {
        window.navigator.chrome = {
            runtime: {},
            app: {
                isInstalled: false,
                InstallState: {
                    DISABLED: 'disabled',
                    INSTALLED: 'installed',
                    NOT_INSTALLED: 'not_installed'
                },
                RunningState: {
                    CANNOT_RUN: 'cannot_run',
                    READY_TO_RUN: 'ready_to_run',
                    RUNNING: 'running'
                }
            },
            csi: function() {
                return {
                    onloadT: Date.now(),
                    pageT: Date.now(),
                    startE: Date.now(),
                    tran: 15
                };
            },
            loadTimes: function() {
                return {
                    requestTime: Date.now() / 1000,
                    startLoadTime: Date.now() / 1000,
                    commitLoadTime: Date.now() / 1000,
                    finishDocumentLoadTime: Date.now() / 1000,
                    finishLoadTime: Date.now() / 1000,
                    firstPaintTime: Date.now() / 1000,
                    firstPaintAfterLoadTime: 0,
                    navigationType: "Other",
                    wasFetchedViaSpdy: false,
                    wasNpnNegotiated: true,
                    npnNegotiatedProtocol: "h2",
                    wasAlternateProtocolAvailable: false,
                    connectionInfo: "h2"
                };
            }
        };
    }

    // 3. 隐藏自动化控制特征
    Object.defineProperty(window, 'chrome', {
        get: () => window.navigator.chrome,
        configurable: true
    });

    // 4. 伪造插件列表
    const mockPlugins = [
        {
            0: {
                type: "application/x-google-chrome-pdf",
                suffixes: "pdf",
                description: "Portable Document Format",
                enabledPlugin: null
            },
            description: "Portable Document Format",
            filename: "internal-pdf-viewer",
            length: 1,
            name: "Chrome PDF Plugin"
        },
        {
            0: {
                type: "application/pdf",
                suffixes: "pdf",
                description: "Portable Document Format",
                enabledPlugin: null
            },
            description: "Portable Document Format",
            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
            length: 1,
            name: "Chrome PDF Viewer"
        },
        {
            0: {
                type: "application/x-nacl",
                suffixes: "",
                description: "Native Client Executable",
                enabledPlugin: null
            },
            1: {
                type: "application/x-pnacl",
                suffixes: "",
                description: "Portable Native Client Executable",
                enabledPlugin: null
            },
            description: "",
            filename: "internal-nacl-plugin",
            length: 2,
            name: "Native Client"
        }
    ];

    Object.defineProperty(navigator, 'plugins', {
        get: likeNative(() => mockPlugins, nativeToStringFunctionString),
        configurable: true
    });

    // 5. 伪造语言设置
    Object.defineProperty(navigator, 'languages', {
        get: likeNative(() => ['en-US', 'en', 'zh-CN', 'zh'], nativeToStringFunctionString),
        configurable: true
    });

    // 6. 权限查询处理
    if (navigator.permissions && navigator.permissions.query) {
        const originalQuery = navigator.permissions.query;
        navigator.permissions.query = likeNative((parameters) => {
            if (parameters.name === "notifications") {
                return Promise.resolve({ state: Notification.permission });
            }
            return originalQuery.call(navigator.permissions, parameters);
        }, nativeToStringFunctionString);
    }

    // 7. 伪造触摸支持
    Object.defineProperty(navigator, 'maxTouchPoints', {
        get: likeNative(() => 0, nativeToStringFunctionString),
        configurable: true
    });

    // 8. 伪造硬件信息
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: likeNative(() => 4, nativeToStringFunctionString),
        configurable: true
    });

    Object.defineProperty(navigator, 'deviceMemory', {
        get: likeNative(() => 8, nativeToStringFunctionString),
        configurable: true
    });

    // 9. 平台信息
    Object.defineProperty(navigator, 'platform', {
        get: likeNative(() => 'Win32', nativeToStringFunctionString),
        configurable: true
    });

    // 10. 隐藏页面可见性检测
    Object.defineProperty(document, 'hidden', {
        get: likeNative(() => false, nativeToStringFunctionString),
        configurable: true
    });

    Object.defineProperty(document, 'visibilityState', {
        get: likeNative(() => "visible", nativeToStringFunctionString),
        configurable: true
    });

    // 11. 伪造电池 API
    const mockBattery = {
        charging: true,
        chargingTime: 0,
        dischargingTime: Infinity,
        level: 1.0,
        addEventListener: function() {},
        removeEventListener: function() {},
        dispatchEvent: function() {}
    };
    
    if ('getBattery' in navigator) {
        navigator.getBattery = likeNative(() => Promise.resolve(mockBattery), nativeToStringFunctionString);
    }

    // 12. 覆盖 WebGL 指纹
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
            return 'Intel Inc.';
        }
        if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL  
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter.call(this, parameter);
    };

    // 13. 覆盖 Canvas 指纹
    const toDataURL = HTMLCanvasElement.prototype.toDataURL;
    const toBlob = HTMLCanvasElement.prototype.toBlob;
    const getImageData = CanvasRenderingContext2D.prototype.getImageData;
    
    // 添加噪声到 Canvas
    function addCanvasNoise(imageData) {
        const data = imageData.data;
        for (let i = 0; i < data.length; i += 4) {
            if (Math.random() < 0.001) {
                data[i] = (data[i] + Math.random() * 10 - 5) % 256;
                data[i + 1] = (data[i + 1] + Math.random() * 10 - 5) % 256;
                data[i + 2] = (data[i + 2] + Math.random() * 10 - 5) % 256;
            }
        }
    }

    HTMLCanvasElement.prototype.toDataURL = function(...args) {
        const context = this.getContext('2d');
        if (context) {
            const imageData = context.getImageData(0, 0, this.width, this.height);
            addCanvasNoise(imageData);
            context.putImageData(imageData, 0, 0);
        }
        return toDataURL.apply(this, args);
    };

    // 14. 音频上下文指纹保护
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
        const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
        AudioContext.prototype.createAnalyser = function() {
            const analyser = originalCreateAnalyser.call(this);
            const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
            analyser.getFloatFrequencyData = function(array) {
                originalGetFloatFrequencyData.call(this, array);
                // 添加微小噪声
                for (let i = 0; i < array.length; i++) {
                    array[i] += Math.random() * 0.0001 - 0.00005;
                }
            };
            return analyser;
        };
    }

    // 15. 时区和日期
    Date.prototype.getTimezoneOffset = likeNative(() => -480, nativeToStringFunctionString); // UTC+8

    // 16. 屏幕信息伪造
    Object.defineProperty(screen, 'width', {
        get: likeNative(() => 1920, nativeToStringFunctionString)
    });
    Object.defineProperty(screen, 'height', {
        get: likeNative(() => 1080, nativeToStringFunctionString)
    });
    Object.defineProperty(screen, 'availWidth', {
        get: likeNative(() => 1920, nativeToStringFunctionString)
    });
    Object.defineProperty(screen, 'availHeight', {
        get: likeNative(() => 1040, nativeToStringFunctionString)
    });
    Object.defineProperty(screen, 'colorDepth', {
        get: likeNative(() => 24, nativeToStringFunctionString)
    });
    Object.defineProperty(screen, 'pixelDepth', {
        get: likeNative(() => 24, nativeToStringFunctionString)
    });

    // 17. 媒体设备伪造
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
        const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
        navigator.mediaDevices.enumerateDevices = likeNative(() => {
            return Promise.resolve([
                {
                    deviceId: "default",
                    kind: "audioinput",
                    label: "Default - Microphone (Built-in)",
                    groupId: "group1"
                },
                {
                    deviceId: "default",
                    kind: "audiooutput", 
                    label: "Default - Speaker (Built-in)",
                    groupId: "group1"
                },
                {
                    deviceId: "default",
                    kind: "videoinput",
                    label: "Default - Camera (Built-in)",
                    groupId: "group2"
                }
            ]);
        }, nativeToStringFunctionString);
    }

    // 18. 字体检测绕过
    document.fonts = {
        ready: Promise.resolve(),
        status: 'loaded',
        check: () => true,
        load: () => Promise.resolve([]),
        forEach: () => {},
        values: () => [],
        entries: () => []
    };

    // 19. 连接信息
    if ('connection' in navigator) {
        Object.defineProperty(navigator.connection, 'effectiveType', {
            get: likeNative(() => '4g', nativeToStringFunctionString)
        });
        Object.defineProperty(navigator.connection, 'downlink', {
            get: likeNative(() => 10, nativeToStringFunctionString)
        });
        Object.defineProperty(navigator.connection, 'rtt', {
            get: likeNative(() => 50, nativeToStringFunctionString)
        });
    }

    // 20. 防止检测脚本执行
    const originalEval = window.eval;
    window.eval = function(code) {
        // 检查是否包含常见的检测代码
        if (typeof code === 'string' && (
            code.includes('webdriver') ||
            code.includes('automation') ||
            code.includes('phantom') ||
            code.includes('selenium')
        )) {
            return undefined;
        }
        return originalEval.call(this, code);
    };

    // 21. 隐藏Iframe检测
    Object.defineProperty(window, 'top', {
        get: likeNative(() => window, nativeToStringFunctionString)
    });

    // 22. 防止堆栈跟踪检测
    Error.prepareStackTrace = function(error, stack) {
        return stack.filter(frame => 
            !frame.getFileName() || 
            !frame.getFileName().includes('chrome-extension://') &&
            !frame.getFileName().includes('extensions/')
        ).map(frame => frame.toString()).join('\n');
    };

    console.log('🛡️ Enhanced anti-detection script loaded successfully');
})();
