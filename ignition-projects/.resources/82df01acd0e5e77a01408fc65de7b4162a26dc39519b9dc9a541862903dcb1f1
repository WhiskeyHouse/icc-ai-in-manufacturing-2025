def doGet(request, session):
	html = """
<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PanZoomIframe</title>
    <style>
        body {
            overflow: hidden;
        }

        div {
            touch-action: none;
            user-select: none;
        }

        iframe {
            transform-origin: 0 0;
            position: absolute;
            width: 100%;
            height: 100%;
            touch-action: none;
            overflow: visible;
            border: none;
        }

        button:hover {
            fill: dodgerblue;
        }

        @media (hover: none) {
            button:hover {
                fill: black;
            }
        }

        .disableButton {
            fill: grey;
        }

        select {
            width: 72px;
            height: auto;
            margin: 4px;
            user-select: none;
            background-color: transparent;
            border: solid;
            border-width: 1px;
            border-radius: 8px;
        }

        select>option {
            background-color: lightgray;
            border: solid;
            border-width: 1px;
            border-radius: 8px;
        }

        select:focus {
            outline: none;
        }

        #everything {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }

        #content {
            transform-origin: 0 0;
            transition: all 0ms;
            position: absolute;

            width: 100%; /*replace-width*/
            height: 100%; /*replace-height*/

            border: none;
        }

        #overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: block;
        }


        #controls {
            position: absolute;
            width: 400px;
            height: auto;
            display: flex;
            align-items: stretch;
            justify-content: space-between;
            background-color: lightgray;
            border-radius: 8px;
            opacity: 0.9;
            box-sizing: border-box;
            margin: 4px;
        }

        #controls button {
            aspect-ratio: 1 / 1;
            flex-grow: 0;
            flex-shrink: 1;
            flex-basis: 48px;
            max-width: 64px;
            max-height: 64px;
            object-fit: contain;
            overflow: hidden;
            box-sizing: border-box; 
            cursor: pointer;
            user-select: none;
            margin: 4px;
            border: none;
            background-color: transparent;
            border-radius: 8px;
        }

        #controls #pan-interact button {
            margin: 0px;
        }

        #controls svg {
            aspect-ratio: 1 / 1;
            width: 100%;
            height: 100%;
            max-width: 64px;
            max-height: 64px;
            object-fit: contain;
            overflow: hidden;
            box-sizing: border-box; 
            cursor: pointer;
            user-select: none;
            margin: 0px;
            padding: 0px;
        }

        #pan-interact {
            flex-grow: 0;
            flex-shrink: 1;
            flex-basis: 100px;
            overflow: hidden;
            margin: 4px;
            border-radius: 8px;
            background-color: darkgrey; 
            display: flex;
            align-items: stretch;
            justify-content: space-between;
        }

        #info-dock {
            display: flex;
            flex-direction: column;
            position: absolute;
            top: 60px;
            border-radius: 8px;
            margin: 4px;
            height: 0px;
            width: 272px;
            transition: height 250ms linear;
            background-color: lightgrey;
            box-sizing: border-box;
            overflow: hidden;
            font-family: Arial, Helvetica, sans-serif;
            opacity: 0.9;
        }

        .info-item {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            margin: 4px;
            height: 80px;
        }

        .info-item svg {
            flex-basis: 48px;
            margin: 4px;
            padding-right: 24px;
        }

        .info-item #list-dummy {
            flex-basis: 60px;
            margin-right: 16px;
            margin-left: 4px;
            height: 48px;
        }

        @media screen and (max-width: 640px) {
            #controls {
                position: absolute;
                top: auto;
                bottom: 8px;
                height: auto;
                width: 100%;
                margin: 0px;
                align-items: stretch;
            }

            #controls button {
                margin: 0px;
            }

            #info-dock {
                bottom: 64px;
                top: auto;
            }
        }

    </style>
</head>

<svg style="display:none;">
    <defs>
        <svg id="fit-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" preserveAspectRatio="xMidYMid">
            <path
                d="M15,3l2.3,2.3l-2.89,2.87l1.42,1.42L18.7,6.7L21,9V3H15z M3,9l2.3-2.3l2.87,2.89l1.42-1.42L6.7,5.3L9,3H3V9z M9,21 l-2.3-2.3l2.89-2.87l-1.42-1.42L5.3,17.3L3,15v6H9z M21,15l-2.3,2.3l-2.87-2.89l-1.42,1.42l2.89,2.87L15,21h6V15z" />
        </svg>
        <svg id="zoom-out-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" preserveAspectRatio="xMidYMid">
            <path
                d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14zM7 9h5v1H7z" />
        </svg>
        <svg id="zoom-in-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" preserveAspectRatio="xMidYMid">
            <path
                d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
            <path d="M12 10h-2v2H9v-2H7V9h2V7h1v2h2v1z" />
        </svg>
        <svg id="pan-icon" xmlns="http://www.w3.org/2000/svg" viewBox="-1 -2 28 28" preserveAspectRatio="xMidYMid">
            <path
                d="M23,5.5V20c0,2.2-1.8,4-4,4h-7.3c-1.08,0-2.1-0.43-2.85-1.19L1,14.83c0,0,1.26-1.23,1.3-1.25 c0.22-0.19,0.49-0.29,0.79-0.29c0.22,0,0.42,0.06,0.6,0.16C3.73,13.46,8,15.91,8,15.91V4c0-0.83,0.67-1.5,1.5-1.5S11,3.17,11,4v7 h1V1.5C12,0.67,12.67,0,13.5,0S15,0.67,15,1.5V11h1V2.5C16,1.67,16.67,1,17.5,1S19,1.67,19,2.5V11h1V5.5C20,4.67,20.67,4,21.5,4 S23,4.67,23,5.5z" />
        </svg>
        <svg id="interact-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 2 24 24" preserveAspectRatio="xMidYMid">
            <path
                d="M9,11.24V7.5C9,6.12,10.12,5,11.5,5S14,6.12,14,7.5v3.74c1.21-0.81,2-2.18,2-3.74C16,5.01,13.99,3,11.5,3S7,5.01,7,7.5 C7,9.06,7.79,10.43,9,11.24z M18.84,15.87l-4.54-2.26c-0.17-0.07-0.35-0.11-0.54-0.11H13v-6C13,6.67,12.33,6,11.5,6 S10,6.67,10,7.5v10.74c-3.6-0.76-3.54-0.75-3.67-0.75c-0.31,0-0.59,0.13-0.79,0.33l-0.79,0.8l4.94,4.94 C9.96,23.83,10.34,24,10.75,24h6.79c0.75,0,1.33-0.55,1.44-1.28l0.75-5.27c0.01-0.07,0.02-0.14,0.02-0.2 C19.75,16.63,19.37,16.09,18.84,15.87z" />
        </svg>
        <svg id="close-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" preserveAspectRatio="xMidYMid">
            <path
                d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
        </svg>
        <svg id="info-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" preserveAspectRatio="xMidYMid">
            <path d="M453-280h60v-240h-60v240Zm26.982-314q14.018 0 23.518-9.2T513-626q0-14.45-9.482-24.225-9.483-9.775-23.5-9.775-14.018 0-23.518 9.775T447-626q0 13.6 9.482 22.8 9.483 9.2 23.5 9.2Zm.284 514q-82.734 0-155.5-31.5t-127.266-86q-54.5-54.5-86-127.341Q80-397.681 80-480.5q0-82.819 31.5-155.659Q143-709 197.5-763t127.341-85.5Q397.681-880 480.5-880q82.819 0 155.659 31.5Q709-817 763-763t85.5 127Q880-563 880-480.266q0 82.734-31.5 155.5T763-197.684q-54 54.316-127 86Q563-80 480.266-80Zm.234-60Q622-140 721-239.5t99-241Q820-622 721.188-721 622.375-820 480-820q-141 0-240.5 98.812Q140-622.375 140-480q0 141 99.5 240.5t241 99.5Zm-.5-340Z"/>
        </svg>
    </defs>
</svg>

<body>
    <div id="everything">
        <div id="content">
            <iframe id="simple-view"></iframe>
            <iframe id="detailed-view"></iframe>
        </div>
        <div id="overlay"></div>
        <div id="controls">
            <button onclick="fit()"><svg><use href="#fit-icon" /></svg></button>
            <button onclick="zoomOut()"><svg><use href="#zoom-out-icon" /></svg></button>
            <button onclick="zoomIn()"><svg><use href="#zoom-in-icon" /></svg></button>
            <select id="list" onchange="zoomList(this.value)">
                <option selected disabled hidden>100%</option>
                <option value="25">25%</option>
                <option value="50">50%</option>
                <option value="100">100%</option>
                <option value="200">200%</option>
                <option value="400">400%</option>
            </select>
            <div id = pan-interact>
                <button id="pan-button" onclick="pan()"><svg><use href="#pan-icon" /></svg></button>
                <button id="interact-button" onclick="interact()"><svg><use href="#interact-icon" /></svg></button>
            </div>
            <button id="info-button" onclick="toggleInfo()"><svg><use href="#info-icon" /></svg></button>
        </div>
        <div id="info-dock">
            <div class="info-item">
                <svg><use href="#fit-icon" /></svg>
                <span>Fit to screen</span>
            </div>
            <div class="info-item">
                <svg><use href="#zoom-out-icon" /></svg>
                <span>Zoom Out</span>
            </div>
            <div class="info-item">
                <svg><use href="#zoom-in-icon" /></svg>
                <span>Zoom In</span>
            </div>
            <div class="info-item">
                <select id="list-dummy" disabled>
                    <option selected disabled hidden>100%</option>
                </select>
                <span>Set Zoom</span>
            </div>
            <div class="info-item">
                <svg><use href="#pan-icon" /></svg>
                <span>Panning Mode
                    <br>&emsp;Interact : Disabled
                    <br>&emsp;Pan : Any Mouse Click
                    <br>&emsp;Zoom : Scroll Wheel
                </span>
            </div>
            <div class="info-item">
                <svg><use href="#interact-icon" /></svg>
                <span>Interactive Mode
                    <br>&emsp;Interact : Left Click
                    <br>&emsp;Pan : Disabled
                    <br>&emsp;Zoom : Control Buttons
                </span>
            </div>
        </div>
        
    </div>
    <script>

        // #region - global variables
        var targetSimple = 'https://example.com/'; /*replace-target*/
        var targetDetailed = ''; /*replace-target-detailed*/

        var content = document.getElementById('content');
        var overlay = document.getElementById('overlay');
        var simpleView = document.getElementById('simple-view');
        var detailedView = document.getElementById('detailed-view');
        var buttons = document.querySelectorAll('button');
        var list = document.getElementById('list');
        var panButton = document.getElementById('pan-button');
        var interactButton = document.getElementById('interact-button');
        var infoButton = document.getElementById('info-button');
        var infoDock = document.getElementById('info-dock');
        var controls = document.getElementById('controls');

        var scale = 1;
        var originX = 0;
        var originY = 0;
        var startPosX = 0;
        var startPosY = 0;
        var initialDistance = 0;
        var pointerOffset = 0;
        var showInfo = false;

        // #endregion

        // #region - on startup
        window.onload = function () {
            simpleView.src = targetSimple
            detailedView.src = targetDetailed
            detailedView.style.display = 'none';

            setPan();
            fit();
        }

        window.addEventListener('contextmenu', function (e) {
            e.preventDefault();
        });

        // #endregion

        // #region - common functions
        function updateStyle(durationMS = 0) {
            let transition = 'all ' + durationMS + 'ms ';
            content.style.transition = transition;
            toggleInfo(forceClose = true);

            content.style.transform = 'scale(' + scale + ') translate(' + originX + 'px,' + originY + 'px)';
            if (targetDetailed !== "") {
                if (scale >= 2) {
                    detailedView.style.display = 'block';
                    simpleView.style.display = 'none';
                } else {
                    simpleView.style.display = 'block';
                    detailedView.style.display = 'none';
                }
            }

            /* update placeholder value */
            list.options[0].text = Math.round(scale * 100) + '%';
            list.selectedIndex = 0;
        }

        function setZoom(dynamicZoom = 0, staticZoom = 1, x = window.innerWidth / 2, y = window.innerHeight / 2) {
            originalScale = scale;

            if (dynamicZoom != 0) {
                scale *= dynamicZoom;
            } else {
                scale = staticZoom;
            }

            originX += x / scale - x / originalScale;
            originY += y / scale - y / originalScale;

            updateStyle();
        }

        function setPan(isPan = true) {
            if (isPan) {
                overlay.style.display = 'block';

                panButton.style.border = 'solid';
                panButton.style.borderWidth = '1px';
                panButton.style.fill = 'black';
                panButton.classList.remove('disableButton');

                interactButton.style = null;
                interactButton.classList.add('disableButton');
            } else {
                overlay.style.display = 'none';

                panButton.style = null;
                panButton.classList.add('disableButton');

                interactButton.style.border = 'solid';
                interactButton.style.borderWidth = '1px';
                interactButton.style.fill = 'black';
                interactButton.classList.remove('disableButton');
            }
        }

        function locate(w, h, left = 0, top = 0, doZoom = true, scaleAugment = 1) {
            /* this function locates the element on screen */
            let minScale = scale;
            if (doZoom) {
                let scaleX = window.innerWidth / w;
                let scaleY = window.innerHeight / h;
                minScale = Math.min(scaleX, scaleY) * scaleAugment;
            }

            let x = (window.innerWidth / minScale - w) / 2 - left;
            let y = (window.innerHeight / minScale - h) / 2 - top;

            return [minScale, x, y]
        }
        // #endregion

        // #region - mouse controls
        overlay.addEventListener('wheel', function (e) {
            e.preventDefault();

            let newZoom = 1;
            if (e.deltaY > 0) {
                newZoom /= 1.1;
            } else {
                newZoom *= 1.1;
            }

            let x = e.clientX - pointerOffset;
            let y = e.clientY - pointerOffset;

            setZoom(newZoom, 0, x, y);
        }, { passive: false });

        overlay.onmousedown = function (e) {
            e.preventDefault();
            startPosX = e.clientX;
            startPosY = e.clientY;

            document.onmousemove = function (e) {
                e.preventDefault();
                originX += (e.clientX - startPosX) / scale;
                originY += (e.clientY - startPosY) / scale;
                updateStyle();
                startPosX = e.clientX;
                startPosY = e.clientY;
            }

            document.onmouseup = function () {
                document.onmousemove = null;
                document.onmouseup = null;
            }
        }
        // #endregion

        // #region - touch controls
        overlay.addEventListener('touchstart', function (e) {
            if (e.target.id == 'clickable-item') {
                // insert logic here
            } else {
                e.preventDefault();
            }
            cachePosition(e);
        }, { passive: false });

        overlay.addEventListener('touchmove', function (e) {
            e.preventDefault();
            if (e.touches.length == 1) {  // one finger is touching
                originX += (e.touches[0].clientX - startPosX) / scale;
                originY += (e.touches[0].clientY - startPosY) / scale;
                startPosX = e.touches[0].clientX;
                startPosY = e.touches[0].clientY;
            } else if (e.touches.length == 2) { // two fingers are touching
                let currentDistance = Math.hypot(
                    e.touches[0].clientX - e.touches[1].clientX,
                    e.touches[0].clientY - e.touches[1].clientY
                );
                if (initialDistance != 0) {
                    let originalScale = scale;
                    let midX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
                    let midY = (e.touches[0].clientY + e.touches[1].clientY) / 2

                    let x = midX - pointerOffset;
                    let y = midY - pointerOffset;

                    scale *= currentDistance / initialDistance;

                    // zoom at center
                    originX += x / scale - x / originalScale + (midX - startPosX) / scale;
                    originY += y / scale - y / originalScale + (midY - startPosY) / scale;

                    startPosX = midX;
                    startPosY = midY;
                }
                initialDistance = currentDistance;
            }
            updateStyle();
        }, { passive: false });

        overlay.addEventListener('touchend', function (e) {
            if (e.target.id == 'clickable-item') {
                // insert logic here
            } else {
                e.preventDefault();
            }
            cachePosition(e);
        }, { passive: false });

        function cachePosition(e) {
            if (e.touches.length == 0) {
                startPosX = 0;
                startPosY = 0;
                initialDistance = 0;
            } else if (e.touches.length == 1) {
                startPosX = e.touches[0].clientX;
                startPosY = e.touches[0].clientY;
                initialDistance = 0;
            } else if (e.touches.length == 2) {
                startPosX = (e.touches[0].clientX + e.touches[1].clientX) / 2;
                startPosY = (e.touches[0].clientY + e.touches[1].clientY) / 2;

                initialDistance = Math.hypot(
                    e.touches[0].clientX - e.touches[1].clientX,
                    e.touches[0].clientY - e.touches[1].clientY
                );
            }
        }
        // #endregion

        // #region - buttons

        /*  
            fix default button behavior on touchscreen
            even if touch moves slightly it will still register as a click
            as long as when touch ended it was within the button bounds
            this mimics how default button mouse clicks work
        */
        buttons.forEach(function (button) {
            button.addEventListener('touchend', function (e) {
                var touch = e.changedTouches[0];
                var rect = this.getBoundingClientRect();
                if (touch.clientX >= rect.left && touch.clientX <= rect.right &&
                    touch.clientY >= rect.top && touch.clientY <= rect.bottom) {

                    if (e.cancelable) {
                        e.preventDefault();
                    }
                    this.click();
                }
            }, { passive: false });
        });

        function fit() {
            [scale, originX, originY] = locate(content.offsetWidth, content.offsetHeight);

            updateStyle(500);
        }

        function zoomOut() {
            setZoom(1 / 1.1);
        }

        function zoomIn() {
            setZoom(1.1);
        }

        function zoomList(value) {
            setZoom(0, value / 100);
        }

        function pan() {
            setPan();
        }

        function interact() {
            setPan(false);
        }

        function toggleInfo(forceClose = false) {
            let svgUse = infoButton.getElementsByTagName("use")[0]
            if (showInfo || forceClose){
                infoDock.style.height = '0px';
                svgUse.setAttribute("href", "#info-icon");
                showInfo = false;
            } else {
                infoDock.style.height = '550px';
                svgUse.setAttribute("href", "#close-icon");
                showInfo = true;
            }
        }

        // #endregion
    </script>
</body>

</html>
	"""
	
	gatewayAddress = request['params'].get('gatewayAddress', '')
	projectName = request['params'].get('projectName', '')
	targetUrl = request['params'].get('targetUrl', '')
	targetDetailedUrl = request['params'].get('targetDetailedUrl', '')
	height = request['params'].get('height', '')
	width = request['params'].get('width', '')
	
	def makeURL(page):
		if page.startswith('/'):
			URL = "'{gatewayAddress}/data/perspective/client/{projectName}{page}';".format(gatewayAddress=gatewayAddress, projectName=projectName, page=page)
		else:
			URL = "'{page}';".format(page=page)
		return URL
	
	def cleanDim(dim):
		if dim == '':
			iDim = '100%'
		elif dim.endswith('%'):
			iDim = dim
		elif dim.endswith('px'):
			iDim = dim
		else:
			iDim = '%spx' % dim
		return '%s;' % iDim
	
	html = html.replace("'https://example.com/'; /*replace-target*/", makeURL(targetUrl))
	html = html.replace("''; /*replace-target-detailed*/", makeURL(targetDetailedUrl))
	html = html.replace("100%; /*replace-width*/", cleanDim(width))
	html = html.replace("100%; /*replace-height*/", cleanDim(height))
	
	return {'html': html}