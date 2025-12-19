<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Heading from '$lib/components/Heading.svelte';

	const { Story } = defineMeta({
		title: 'Components/Heading',
		component: Heading,
		parameters: {
			layout: 'centered'
		}
	});
</script>

<Story name="Purple" args={{ title: 'Purple', color: 'purple' }} />
<Story name="Blue" args={{ title: 'Blue', color: 'blue' }} />
<Story name="Green" args={{ title: 'Green', color: 'green' }} />
<Story name="Yellow" args={{ title: 'Yellow', color: 'yellow' }} />
<Story name="Orange" args={{ title: 'Orange', color: 'orange' }} />
<Story name="Pink" args={{ title: 'Pink', color: 'pink' }} />
