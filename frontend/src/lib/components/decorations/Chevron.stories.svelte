<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Chevron from '$lib/components/decorations/Chevron.svelte';

	const { Story } = defineMeta({
		title: 'Components/Chevron',
		component: Chevron,
		parameters: {
			layout: 'centered'
		}
	});
</script>

<Story name="Default" args={{ class: '' }} />
