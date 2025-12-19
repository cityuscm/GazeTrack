<script lang="ts">
	import { currentPage } from '../contexts.svelte.ts';

	let page = $derived.by(() => {
		try {
			return currentPage.get();
		} catch (e) {
			return 'Controller';
		}
	});
</script>

<div
	class="p-4 pt-4 w-full z-50 flex flex-col gap-2 text-white text-shadow text-shadow-color-black text-shadow-blur-2xl
	md:(pl-8 pt-8 mb-20)
	xl:(pl-12 pt-12 mb-24)"
>
	<span class="text-lg md:text-xl xl:text-2xl font-thin">GazeTrack</span>
	<span class="text-xl md:text-2xl xl:text-4xl font-thin">{page}</span>
</div>
