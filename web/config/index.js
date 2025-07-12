const { createApp, reactive, ref, onMounted } = Vue;
const deepClone = obj => JSON.parse(JSON.stringify(obj));
window.addEventListener('pywebviewready', function () {
    window.pywebview = pywebview;
    console.log({ pywebview });
})
Validator.register("custom-url", (value) => /^https?:\/\/(?:localhost|\d{1,3}(?:\.\d{1,3}){3}|(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,63})(?::\d{1,5})?(?:\/[^\s]*)?$/i.test(value), "Invalid URL format");
createApp({
    setup() {
        const deviceTypes = ['desktop', 'laptop', 'handheld', 'server'];
        const serviceTypes = ['web', 'code', 'database', 'file', 'video', 'remote-control', 'ssh', 'dev-server', 'other'];
        const defaultC = { name: '', appKey: '', backendUrl: '', type: 'desktop', enableDiscordRPC: false, includeDockerServices: false, disableNotifications: false, services: [], actionables: [] };
        const config = reactive(deepClone(defaultC));
        const errors = reactive({});
        const hasApi = ref(false);
        const loading = ref(false);
        const fileInput = ref(null);

        const baseRules = { name: 'required', appKey: 'required', backendUrl: 'required|custom-url', type: `required|in:${deviceTypes.join(',')}` };
        const baseRulesMessages = {
            required: "Field is required",
            url: "Invalid URL format",
            in: "Field must be one of: :values",
            integer: "Field must be an integer",
            min: "Field must be at least :min",
            max: "Field must be at most :max",
        }

        function validateAll() {
            const data = { ...config };
            config.services.forEach((s, i) => {
                data[`services.${i}.id`] = s.id; data[`services.${i}.name`] = s.name;
                data[`services.${i}.port`] = s.port; data[`services.${i}.type`] = s.type;
            });
            config.actionables.forEach((a, i) => {
                data[`actionables.${i}.name`] = a.name;
                data[`actionables.${i}.action`] = a.action;
            });

            const rules = { ...baseRules };
            config.services.forEach((_, i) => {
                rules[`services.${i}.name`] = 'required';
                rules[`services.${i}.port`] = 'required|integer|min:1|max:65535';
                rules[`services.${i}.type`] = `required|in:${serviceTypes.join(',')}`;
            });
            config.actionables.forEach((_, i) => {
                rules[`actionables.${i}.name`] = 'required';
                rules[`actionables.${i}.action`] = 'required';
            });

            const v = new Validator(data, rules, baseRulesMessages);
            if (v.fails()) {
                Object.assign(errors, v.errors.all());
                return false;
            }
            Object.keys(errors).forEach(k => delete errors[k]);
            return true;
        }

        function validateField(field) {
            const val = {};
            val[field] = get(config, field);
            const rul = {};
            rul[field] = getRule(field);
            const v = new Validator(val, rul, baseRulesMessages);
            if (v.fails()) errors[field] = v.errors.get(field);
            else delete errors[field];
        }

        function getRule(field) {
            if (field.startsWith('services')) return field.endsWith('port') ? 'required|integer|min:1|max:65535'
                : field.endsWith('type') ? `required|in:${serviceTypes.join(',')}` : 'required';
            if (field.startsWith('actionables')) return 'required';
            return baseRules[field] || '';
        }

        function inputCls(field) {
            return [
                'w-full px-3 py-2 bg-input border rounded-md  ring-green-custom text-white',
                errors[field] ? 'border-red-500' : 'border-input'
            ].join(' ');
        }

        function get(obj, path) { return path.split('.').reduce((o, k) => o?.[k], obj); }

        function addService() { config.services.push({ id: "srv-" + config.services.length + 1, name: '', port: '', type: 'web' }); }
        function removeService(i) { config.services.splice(i, 1); }
        function addActionable() { config.actionables.push({ name: '', action: '' }); }
        function removeActionable(i) { config.actionables.splice(i, 1); }

        function loadFile(e) {
            const file = e.target.files[0];
            if (!file || file.type !== 'application/json') return alert('Invalid json file. Please select a valid JSON file.');
            const r = new FileReader();
            r.onload = ev => {
                try {
                    Object.assign(config, deepClone(defaultC), JSON.parse(ev.target.result));
                    Object.keys(errors).forEach(k => delete errors[k]);
                } catch (err) { alert('Error parsing JSON: ' + err.message); }
            };
            r.readAsText(file);
            e.target.value = '';
        }

        function downloadJSON() {
            if (!validateAll()) return alert('There are validation errors. Please fix them before saving.');
            const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
            const downloadAnchor = document.createElement('a');
            downloadAnchor.href = URL.createObjectURL(blob);
            downloadAnchor.download = 'config.json';
            downloadAnchor.click();
            URL.revokeObjectURL(downloadAnchor.href);
        }

        function handleSave() {
            if (!validateAll()) return alert('There are validation errors. Please fix them before saving.');
            loading.value = true;
            window.pywebview.api.saveData(config)
                .then(() => {
                    alert('Configuration saved successfully!');
                    setTimeout(() => {
                        loading.value = false;
                    }, 4000);
                });
        }

        function waitForPyWebview() {
            const start = Date.now();
            const maxWait = 10000;
            const interval = setInterval(() => {
                if (window.pywebview && window.pywebview.api) {
                    clearInterval(interval);
                    hasApi.value = true;
                    window.pywebview.api.getData().then(c => {
                        console.log('Config data received:', c);
                        Object.assign(config, deepClone(defaultC), c.data);
                        Object.keys(errors).forEach(k => delete errors[k]);
                    });
                } else if (Date.now() - start > maxWait) {
                    clearInterval(interval);
                    console.warn("pywebview not detected after 5 seconds.");
                }
            }, 100);
        }

        onMounted(() => {
            waitForPyWebview();
            lucide.createIcons();
        });

        return {
            config, errors, loading, fileInput, deviceTypes, serviceTypes, hasApi,
            addService, removeService, addActionable, removeActionable,
            loadFile, downloadJSON, handleSave,
            validateField, inputCls
        };
    }
}).mount('#app');