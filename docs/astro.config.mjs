// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightSidebarTopicsPlugin from 'starlight-sidebar-topics';
import starlightHeadingBadgesPlugin from 'starlight-heading-badges';

// https://astro.build/config
export default defineConfig({
	site: 'https://cityuscm.github.io',
	base: '/GazeTrack',
	integrations: [
		starlight({
			title: 'GazeTrack',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/withastro/starlight' }],
			plugins: [
				starlightHeadingBadgesPlugin(),
				starlightSidebarTopicsPlugin([
					{
						label: 'Home',
						link: '/home/',
						icon: 'open-book',
						items: [
							{label: 'Home', link: '/home/'},
							{label: 'Getting Started', link: '/home/getting-started'},
							{label: 'Installation', link: '/home/installation'},
							{label: 'Using the Prebuilt App', link: '/home/using-the-prebuilt-app'},
						]
					},
					{
						label: 'Core',
						link: '/core/',
						icon: 'puzzle',
						items: [
							{label: 'Core Runtime API', link: '/core/'},
							{
								label: 'Reference',
								autogenerate: { directory: 'core/reference' },
							}
						]
					},
					{
						label: 'Web UI',
						link: '/webui/',
						icon: 'seti:svelte',
						items: [
							{label: 'Web UI', link: '/webui/'}
						]
					}
				])
			]
		}),
	],
});
