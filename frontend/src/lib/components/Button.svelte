<script lang="ts">
	import Chevron from '$lib/components/decorations/Chevron.svelte';
	import SelectionIndicator from '$lib/components/decorations/SelectionIndicator.svelte';
	import { watch } from 'runed';

	interface Props {
		name: string;
		address?: string;
		type?: 'button' | 'toggle';
		selected?: boolean;
		onclick?: () => void;
	}

	let { name, address, type = 'button', selected = $bindable(false), onclick }: Props = $props();

	const displayAddress = $derived(address ?? 'Unlisted');

	const clickCallback = $derived(type === 'toggle' ? () => (selected = !selected) : onclick);

	const selectedCss = $derived(
		selected ? 'filter-brightness-105 translate-0!' : 'hover:(filter-brightness-110 -translate-2)'
	);

	const overlayCss = $derived(
		type === 'button'
			? 'group-hover:(filter-brightness-110 -translate-2) group-active:(filter-brightness-105 translate-0!)'
			: selectedCss
	);

	const backdropOpacity = $derived(
		type === 'button' ? 'opacity-0' : selected ? 'opacity-100' : 'opacity-0'
	);

	watch(
		() => type,
		() => {
			if (type === 'toggle') {
				selected = false;
			}
		}
	);
</script>

<button
	onclick={clickCallback}
	class="relative group flex flex-row items-start justify-between min-w-60 min-h-16 w-full p-2
	text-gray-50 transition-all duration-200 cursor-pointer"
>
	<span class="parent-size bg-gray-950/50 rounded-md"></span>
	<span class="parent-size -translate-1 {overlayCss} transition-all! duration-200 rounded-md">
		<span
			class="parent-size
			bg-gradient-to-r from-yellow-400 to-yellow-500
			{backdropOpacity}
			group-hover:(opacity-100) group-active:(opacity-100)
			rounded-md transition-all duration-200"
		></span>
		<span
			class="parent-size flex flex-row items-start
			p-1 px-2 rounded-md group-hover:(bg-transparent border-white/50 border-2) transition-all duration-200
			border-2 border-black/50 {selected && type === 'toggle'
				? 'bg-transparent'
				: 'bg-neutral-800'} backdrop-blur-md rounded-md"
		>
			<span
				class="h-full flex-grow flex flex-col items-start text-shadow-2xs text-shadow-color-gray-800/30"
			>
				<span class="font-bold text-lg">{name}</span>
				<span class="text-sm">{displayAddress}</span>
			</span>
			{#if type === 'button'}
				<Chevron class="w-8 h-full" />
			{:else}
				<SelectionIndicator class="w-6 h-full mr-2" {selected} />
			{/if}
		</span>
	</span>
</button>
