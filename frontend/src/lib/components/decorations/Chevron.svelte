<script lang="ts">
	import { waapi } from 'animejs';

	interface Props {
		class?: string;
		count?: number;
		duration?: number;
	}

	const { class: className, count = 3, duration = 2500 }: Props = $props();
	const delays = Array.from({ length: count }, (_, i) => (i * duration) / count);
</script>

<span class="relative inline-block {className}">
	{#each { length: count }, index}
		<span
			class="absolute-center text-3xl i-tabler:chevron-right"
			{@attach (element) => {
				waapi.animate(element, {
					x: ['-50%', '50%'],
					opacity: [0, 1, 0],
					duration,
					ease: 'linear',
					delay: delays[index],
					loop: true
				});
			}}
		></span>
	{/each}
</span>
