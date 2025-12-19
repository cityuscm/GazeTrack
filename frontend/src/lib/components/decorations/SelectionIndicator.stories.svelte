<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import SelectionIndicator from '$lib/components/decorations/SelectionIndicator.svelte';

	const { Story } = defineMeta({
		title: 'Components/SelectionIndicator',
		component: SelectionIndicator,
		parameters: {
			layout: 'centered'
		}
	});
</script>

<Story name="Default" args={{ selected: false, class: 'aspect-square w-6' }} />
