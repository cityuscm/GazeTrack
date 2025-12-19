<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Backdrop from '$lib/components/decorations/Backdrop.svelte';

	const { Story } = defineMeta({
		title: 'Components/Backdrop',
		component: Backdrop,
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story name="Default" />
