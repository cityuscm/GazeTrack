<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import SceneSelector from './SceneSelector.svelte';

	const { Story } = defineMeta({
		title: 'Layouts/SceneSelector',
		component: SceneSelector,
		parameters: {
			layout: 'fullscreen'
		}
	});
</script>

<Story name="Default" args={{ env: 'test' }} />
