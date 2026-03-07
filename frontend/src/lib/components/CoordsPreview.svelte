<script lang="ts">
	export interface GazeProjection {
		index: number;
		gaze: [number, number];
		offset: [number, number];
	}

	interface Props {
		projections?: GazeProjection[];
	}

	const { projections = [] }: Props = $props();

	const DOT_COLORS = [
		'#4ade80',
		'#60a5fa',
		'#f472b6',
		'#fb923c',
		'#a78bfa',
		'#34d399',
		'#fbbf24',
		'#f87171'
	];

	function offsetToPercent(offset: [number, number]): { left: string; top: string } {
		const left = ((offset[0] + 0.5) * 100).toFixed(2) + '%';
		const top = ((-offset[1] + 0.5) * 100).toFixed(2) + '%';
		return { left, top };
	}
</script>

<div class="relative aspect-square w-full min-w-20">
	<div class="parent-size bg-black/50 rounded-md"></div>
	<div
		class="relative aspect-square w-full bg-green-300/25 backdrop-blur-[2px] rounded-md overflow-hidden border-2 border-green-600 -translate-1"
	>
		<div
			class="absolute inset-0 bg-green-600 bg-mask-hero-graph-paper bg-center mask-position-[61%_61%]"
		></div>
		{#each projections as projection (projection.index)}
			{@const pos = offsetToPercent(projection.offset)}
			{@const color = DOT_COLORS[projection.index % DOT_COLORS.length]}
			<div
				class="absolute w-3 h-3 rounded-full -translate-x-1/2 -translate-y-1/2 shadow-lg ring-2 ring-white/50 transition-[left,top] duration-75"
				style="left: {pos.left}; top: {pos.top}; background-color: {color};"
				title="Client {projection.index}"
			></div>
		{/each}
	</div>
</div>
