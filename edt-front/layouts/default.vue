<template>
    <Menubar :model="items">
      <template #item="{ item, props, hasSubmenu }">
        <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
          <a v-ripple :href="href" v-bind="props.action" @click="navigate">
            <span :class="item.icon" />
            <span>{{ item.label }}</span>
          </a>
        </router-link>
        <a v-else v-ripple :href="item.url" :target="item.target" v-bind="props.action">
          <span :class="item.icon" />
          <span>{{ item.label }}</span>
          <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down" />
        </a>
      </template>
    </Menubar>
    <div class="p-4">
      <slot />
    </div>
</template>

<script setup lang="ts">

const items = ([
  {
    label: 'UniEdt',
    icon: 'i-lucide-home',
    route: '/',
  },
  {
    label: 'Emploi du temps',
    icon: 'i-lucide-book-open',
    route: '/emploi-du-temps',
  },
  {
    label: 'Affichage chronologique',
    icon: 'i-lucide-users',
    route: '/chronologique',
  },
  {
    label: 'Intervenants',
    icon: 'i-lucide-users',
    route: '/intervenants',
  },
])
</script>
