<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Button from '$lib/components/Button.svelte';

	const { Story } = defineMeta({
		title: 'Components/Button',
		component: Button,
		parameters: {
			layout: 'centered'
		}
	});
</script>

<Story name="Default" args={{ name: 'Scene 1', address: '192.168.1.1', type: 'button' }} />

<Story name="Toggle" args={{ name: 'Client 1', address: '192.168.1.1', type: 'toggle' }} />
