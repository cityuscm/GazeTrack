<script lang="ts">
	interface Props {
		selected: boolean;
		class?: string;
	}
	let { selected, class: cls }: Props = $props();
</script>

<div class="flex items-center justify-center {cls}">
	<div class="aspect-square w-full flex items-center justify-center border-2 border-white">
		<span
			class="w-[65%] aspect-square bg-white opacity-0 {selected
				? 'scale-100 opacity-100'
				: 'scale-0 opacity-0'} transition-all duration-200"
		></span>
	</div>
</div>
