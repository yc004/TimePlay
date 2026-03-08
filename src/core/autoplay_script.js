// 自动播放和全屏脚本
(function() {
    console.log('=== 自动播放和全屏脚本 ===');
    
    // 播放所有视频
    function playVideos() {
        var videos = document.getElementsByTagName('video');
        console.log('找到 ' + videos.length + ' 个视频');
        
        for (var i = 0; i < videos.length; i++) {
            var video = videos[i];
            video.muted = false;
            video.autoplay = true;
            video.controls = false;
            
            video.play().then(function() {
                console.log('✓ 视频播放成功');
            }).catch(function(err) {
                console.log('尝试静音播放...');
                video.muted = true;
                video.play();
            });
        }
        return videos.length;
    }
    
    // 点击播放按钮
    function clickPlayButtons() {
        var selectors = [
            'button[class*="play"]',
            'div[class*="play"]',
            '.vjs-big-play-button',
            '[aria-label*="播放"]'
        ];
        
        selectors.forEach(function(sel) {
            document.querySelectorAll(sel).forEach(function(btn) {
                if (btn.offsetParent !== null) {
                    btn.click();
                }
            });
        });
    }
    
    // 强制视频全屏（CSS方式）
    function forceVideoFullscreen(video) {
        console.log('使用CSS强制视频全屏...');
        
        video.style.position = 'fixed';
        video.style.top = '0';
        video.style.left = '0';
        video.style.width = '100vw';
        video.style.height = '100vh';
        video.style.zIndex = '999999';
        video.style.objectFit = 'contain';
        video.style.backgroundColor = '#000';
        
        document.body.style.overflow = 'hidden';
        
        // 隐藏其他元素
        var allElements = document.body.children;
        for (var i = 0; i < allElements.length; i++) {
            if (!allElements[i].contains(video)) {
                allElements[i].style.display = 'none';
            }
        }
        
        console.log('✓ CSS强制全屏已应用');
    }
    
    // 强制播放器全屏
    function forcePlayerFullscreen() {
        console.log('尝试强制播放器全屏...');
        
        // 查找播放器容器
        var playerSelectors = [
            '.player',
            '.video-player',
            '[class*="player"]',
            '[id*="player"]',
            'video'
        ];
        
        var player = null;
        for (var i = 0; i < playerSelectors.length; i++) {
            var elements = document.querySelectorAll(playerSelectors[i]);
            if (elements.length > 0) {
                player = elements[0];
                console.log('找到播放器:', playerSelectors[i]);
                break;
            }
        }
        
        if (player) {
            console.log('应用播放器全屏样式');
            player.style.position = 'fixed';
            player.style.top = '0';
            player.style.left = '0';
            player.style.width = '100vw';
            player.style.height = '100vh';
            player.style.zIndex = '999999';
            player.style.backgroundColor = '#000';
            
            // 如果播放器内有视频，也设置视频样式
            var videos = player.getElementsByTagName('video');
            if (videos.length > 0) {
                console.log('设置视频样式');
                videos[0].style.width = '100%';
                videos[0].style.height = '100%';
                videos[0].style.objectFit = 'contain';
            }
            
            // 隐藏页面其他内容
            document.body.style.overflow = 'hidden';
            var allElements = document.body.children;
            for (var i = 0; i < allElements.length; i++) {
                if (!allElements[i].contains(player) && allElements[i] !== player) {
                    allElements[i].style.display = 'none';
                }
            }
            
            console.log('✓ 播放器全屏已应用');
        } else {
            console.log('未找到播放器，尝试直接全屏视频');
            var videos = document.getElementsByTagName('video');
            if (videos.length > 0) {
                forceVideoFullscreen(videos[0]);
            }
        }
    }
    
    // 点击全屏按钮
    function clickFullscreenButtons() {
        var selectors = [
            'button[class*="fullscreen"]',
            'button[class*="full-screen"]',
            'div[class*="fullscreen"]',
            '[aria-label*="全屏"]',
            '[aria-label*="fullscreen"]',
            '[title*="全屏"]',
            '[title*="fullscreen"]',
            '.vjs-fullscreen-control'
        ];
        
        var clicked = false;
        selectors.forEach(function(sel) {
            if (!clicked) {
                var buttons = document.querySelectorAll(sel);
                buttons.forEach(function(btn) {
                    if (btn.offsetParent !== null && !clicked) {
                        console.log('点击全屏按钮:', sel);
                        btn.click();
                        clicked = true;
                    }
                });
            }
        });
        
        return clicked;
    }
    
    // 立即执行
    playVideos();
    clickPlayButtons();
    
    // 延迟尝试全屏（等待视频加载）
    setTimeout(function() {
        clickFullscreenButtons();
        setTimeout(function() {
            forcePlayerFullscreen();
        }, 1000);
    }, 3000);
    
    // 定期重试播放
    var retries = 0;
    var interval = setInterval(function() {
        if (++retries > 10) {
            clearInterval(interval);
            return;
        }
        playVideos();
        clickPlayButtons();
    }, 2000);
    
    console.log('=== 脚本已激活 ===');
})();
