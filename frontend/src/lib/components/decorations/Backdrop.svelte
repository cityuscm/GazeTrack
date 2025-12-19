<script lang="ts">
</script>

<div class="parent-size">
	<div class="parent-size bg-neutral-800"></div>
	<div class="parent-size bg-mask-hero-topography pattern"></div>
</div>

<style>
	@property --pattern-start {
		syntax: '<color>';
		inherits: false;
		initial-value: hsl(210 80% 55%);
	}

	@property --pattern-end {
		syntax: '<color>';
		inherits: false;
		initial-value: hsl(265 75% 45%);
	}

	@keyframes hue-shift {
		0% {
			--pattern-start: hsl(210 80% 55%);
			--pattern-end: hsl(265 75% 45%);
		}
		50% {
			--pattern-start: hsl(330 75% 60%);
			--pattern-end: hsl(40 85% 55%);
		}
		100% {
			--pattern-start: hsl(210 80% 55%);
			--pattern-end: hsl(265 75% 45%);
		}
	}

	@keyframes opacity-shift {
		from {
			opacity: 0.5;
		}
		to {
			opacity: 0.7;
		}
	}

	.pattern {
		background: linear-gradient(to bottom right, var(--pattern-start), rgba(0,0,0,0), rgba(0,0,0,0), var(--pattern-end));
		animation:
			hue-shift 30s infinite,
			opacity-shift 5s infinite ease-in-out alternate-reverse;
	}
</style>
