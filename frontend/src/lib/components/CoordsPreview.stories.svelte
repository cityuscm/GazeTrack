<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import CoordsPreview from '$lib/components/CoordsPreview.svelte';

	const { Story } = defineMeta({
		title: 'Components/CoordsPreview',
		component: CoordsPreview,
		parameters: {
			layout: 'centered'
		}
	});
</script>

<Story name="Default" args={{}} />
