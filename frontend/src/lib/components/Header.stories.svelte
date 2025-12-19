<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Header from '$lib/components/Header.svelte';

	const { Story } = defineMeta({
		title: 'Components/Header',
		component: Header,
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story name="Default" />
