// Runs before Desk assets. Native startup owns removal; no timers or route hooks.
(() => {
	const container = document.currentScript?.closest(".splash");
	const image = container?.querySelector("[data-reybill-splash]");
	if (!image) return;
	const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
	const fallback = image.dataset.fallback;
	const darkSource = container.querySelector("[data-reybill-splash-dark]");
	const animation = new Image();
	let loaded = false;
	let failed = false;

	function show() {
		if (!image.isConnected) return;
		const playing = !motion.matches && loaded && !failed;
		image.src = playing ? image.dataset.animation : fallback;
		if (darkSource)
			darkSource.srcset = playing ? image.dataset.animation : darkSource.dataset.fallback;
	}

	function load() {
		if (!image.isConnected) return;
		if (!motion.matches && !animation.src && !failed) {
			animation.src = image.dataset.animation;
		}
		show();
	}

	animation.onload = () => {
		loaded = true;
		show();
	};
	animation.onerror = () => {
		failed = true;
		show();
	};
	image.addEventListener("error", () => {
		if (
			image.getAttribute("src") !== fallback ||
			(darkSource && darkSource.getAttribute("srcset") !== darkSource.dataset.fallback)
		) {
			failed = true;
			show();
		}
	});
	if (motion.addEventListener) motion.addEventListener("change", load);
	else motion.addListener(load);
	load();
})();
