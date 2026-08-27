(function (root, factory) {
  "use strict";
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) {
    root.ProfitEngineSiteAgent = api;
    if (root.document) {
      var start = function () {
        try { root.DilivoxSiteAgent = api.createDilivoxSiteAgent(root); }
        catch (_) { root.DilivoxSiteAgent = api.safeAgent("initialization_failed"); }
      };
      if (root.document.readyState === "loading") root.document.addEventListener("DOMContentLoaded", start, {once:true});
      else setTimeout(start, 0);
    }
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  var DEPLOYMENT_VERSION = "task-005-unpublished-v1";
  var SCHEMA_VERSION = "1.0";
  var EVENT_SCHEMA_VERSION = "1.0";
  var MAX_TTL_MS = 30 * 24 * 60 * 60 * 1000;
  var CONTENT = {"/":{"content_id":"e120d0cb-c947-47aa-8ad2-16113a35c928","content_type":"home","slug":"home","active":true},"slug:home":{"content_id":"e120d0cb-c947-47aa-8ad2-16113a35c928","content_type":"home","slug":"home","active":true},"/istorii/":{"content_id":"c9c7a5f3-45bd-464b-9955-d1fa18866884","content_type":"catalog","slug":"stories-list","active":true},"slug:stories-list":{"content_id":"c9c7a5f3-45bd-464b-9955-d1fa18866884","content_type":"catalog","slug":"stories-list","active":true},"/o-proekte/":{"content_id":"551cbbd0-62bc-41af-8436-ff97eef81120","content_type":"about","slug":"about","active":true},"slug:about":{"content_id":"551cbbd0-62bc-41af-8436-ff97eef81120","content_type":"about","slug":"about","active":true},"/kontakty/":{"content_id":"b2fe7e44-fc3c-4ddb-83d2-a428a6d9afe7","content_type":"contacts","slug":"contacts","active":true},"slug:contacts":{"content_id":"b2fe7e44-fc3c-4ddb-83d2-a428a6d9afe7","content_type":"contacts","slug":"contacts","active":true},"/privacy/":{"content_id":"9020f1db-f5ce-4e9b-8c64-f4e3007c9744","content_type":"privacy","slug":"privacy","active":true},"slug:privacy":{"content_id":"9020f1db-f5ce-4e9b-8c64-f4e3007c9744","content_type":"privacy","slug":"privacy","active":true},"/istorii/arhiv-budushchih-prestupleniy/":{"content_id":"50675c31-3c40-4538-925e-6eaab85478e0","content_type":"story","slug":"arhiv-budushchih-prestupleniy","active":true},"slug:arhiv-budushchih-prestupleniy":{"content_id":"50675c31-3c40-4538-925e-6eaab85478e0","content_type":"story","slug":"arhiv-budushchih-prestupleniy","active":true},"/istorii/babushka-protiv-robota-pylesosa/":{"content_id":"f3684352-1517-4235-9fd8-41ca346946dc","content_type":"story","slug":"babushka-protiv-robota-pylesosa","active":true},"slug:babushka-protiv-robota-pylesosa":{"content_id":"f3684352-1517-4235-9fd8-41ca346946dc","content_type":"story","slug":"babushka-protiv-robota-pylesosa","active":true},"/istorii/bilet-do-stantsii-vchera/":{"content_id":"047affae-d42c-4481-8f64-261924653e79","content_type":"story","slug":"bilet-do-stantsii-vchera","active":true},"slug:bilet-do-stantsii-vchera":{"content_id":"047affae-d42c-4481-8f64-261924653e79","content_type":"story","slug":"bilet-do-stantsii-vchera","active":true},"/istorii/bumazhnyy-zhuravl-na-mokrom-stekle/":{"content_id":"89811b55-b3e5-4a0b-9682-93ec6dc95abd","content_type":"story","slug":"bumazhnyy-zhuravl-na-mokrom-stekle","active":true},"slug:bumazhnyy-zhuravl-na-mokrom-stekle":{"content_id":"89811b55-b3e5-4a0b-9682-93ec6dc95abd","content_type":"story","slug":"bumazhnyy-zhuravl-na-mokrom-stekle","active":true},"/istorii/chelyusti-u-buyka-4/":{"content_id":"bd8080e9-18e4-4cba-b9c0-a5537248ac75","content_type":"story","slug":"chelyusti-u-buyka-4","active":true},"slug:chelyusti-u-buyka-4":{"content_id":"bd8080e9-18e4-4cba-b9c0-a5537248ac75","content_type":"story","slug":"chelyusti-u-buyka-4","active":true},"/istorii/chernaya-metka-na-zapyastye/":{"content_id":"5f58e4dd-dcbd-4904-a2b4-c3e8e217869d","content_type":"story","slug":"chernaya-metka-na-zapyastye","active":true},"slug:chernaya-metka-na-zapyastye":{"content_id":"5f58e4dd-dcbd-4904-a2b4-c3e8e217869d","content_type":"story","slug":"chernaya-metka-na-zapyastye","active":true},"/istorii/chernaya-tropa/":{"content_id":"6cbf0fd1-a96d-4da5-8d0a-84023a7ef4bf","content_type":"story","slug":"chernaya-tropa","active":true},"slug:chernaya-tropa":{"content_id":"6cbf0fd1-a96d-4da5-8d0a-84023a7ef4bf","content_type":"story","slug":"chernaya-tropa","active":true},"/istorii/chernyy-konvoy/":{"content_id":"0070ec63-7151-440e-a969-1cf0490df7f5","content_type":"story","slug":"chernyy-konvoy","active":true},"slug:chernyy-konvoy":{"content_id":"0070ec63-7151-440e-a969-1cf0490df7f5","content_type":"story","slug":"chernyy-konvoy","active":true},"/istorii/chernyy-yashchik-imperatritsy/":{"content_id":"6c88dd6f-44b5-4b83-9c5d-f2deda86358b","content_type":"story","slug":"chernyy-yashchik-imperatritsy","active":true},"slug:chernyy-yashchik-imperatritsy":{"content_id":"6c88dd6f-44b5-4b83-9c5d-f2deda86358b","content_type":"story","slug":"chernyy-yashchik-imperatritsy","active":true},"/istorii/chuzhoy-pocherk/":{"content_id":"001f8295-9410-4c72-a4aa-9c39b7ed0eae","content_type":"story","slug":"chuzhoy-pocherk","active":false},"slug:chuzhoy-pocherk":{"content_id":"001f8295-9410-4c72-a4aa-9c39b7ed0eae","content_type":"story","slug":"chuzhoy-pocherk","active":false},"/istorii/desyat-minut-do-granitsy/":{"content_id":"d28e7da9-7625-4e15-b6d9-183c222d6122","content_type":"story","slug":"desyat-minut-do-granitsy","active":true},"slug:desyat-minut-do-granitsy":{"content_id":"d28e7da9-7625-4e15-b6d9-183c222d6122","content_type":"story","slug":"desyat-minut-do-granitsy","active":true},"/istorii/detektivnoe-agentstvo-nu-pochti/":{"content_id":"89823a70-6e44-4319-aee1-d10e9e9b5c9e","content_type":"story","slug":"detektivnoe-agentstvo-nu-pochti","active":true},"slug:detektivnoe-agentstvo-nu-pochti":{"content_id":"89823a70-6e44-4319-aee1-d10e9e9b5c9e","content_type":"story","slug":"detektivnoe-agentstvo-nu-pochti","active":true},"/istorii/devushka-iz-zavtrashnego-chata/":{"content_id":"e8be5709-5c20-4cb3-b036-851e5ef37505","content_type":"story","slug":"devushka-iz-zavtrashnego-chata","active":true},"slug:devushka-iz-zavtrashnego-chata":{"content_id":"e8be5709-5c20-4cb3-b036-851e5ef37505","content_type":"story","slug":"devushka-iz-zavtrashnego-chata","active":true},"/istorii/do-kasaniya/":{"content_id":"d58264de-65c2-41a3-858b-eedb23c1bced","content_type":"story","slug":"do-kasaniya","active":false},"slug:do-kasaniya":{"content_id":"d58264de-65c2-41a3-858b-eedb23c1bced","content_type":"story","slug":"do-kasaniya","active":false},"/istorii/feldsher-na-piratskom-korable/":{"content_id":"f38649ef-035a-4196-9c32-bbf82c97ac89","content_type":"story","slug":"feldsher-na-piratskom-korable","active":true},"slug:feldsher-na-piratskom-korable":{"content_id":"f38649ef-035a-4196-9c32-bbf82c97ac89","content_type":"story","slug":"feldsher-na-piratskom-korable","active":true},"/istorii/golos-v-levom-naushnike/":{"content_id":"27b3767e-5c2c-43e7-8b5a-984ec1a8b370","content_type":"story","slug":"golos-v-levom-naushnike","active":true},"slug:golos-v-levom-naushnike":{"content_id":"27b3767e-5c2c-43e7-8b5a-984ec1a8b370","content_type":"story","slug":"golos-v-levom-naushnike","active":true},"/istorii/gorod-pod-chuzhim-nebom/":{"content_id":"8e827cbc-cd17-4555-9b20-f86e4c55c589","content_type":"story","slug":"gorod-pod-chuzhim-nebom","active":true},"slug:gorod-pod-chuzhim-nebom":{"content_id":"8e827cbc-cd17-4555-9b20-f86e4c55c589","content_type":"story","slug":"gorod-pod-chuzhim-nebom","active":true},"/istorii/gorod-pod-lednikom/":{"content_id":"40ffdc20-5fa5-4e92-a50b-e25d17d23cd7","content_type":"story","slug":"gorod-pod-lednikom","active":true},"slug:gorod-pod-lednikom":{"content_id":"40ffdc20-5fa5-4e92-a50b-e25d17d23cd7","content_type":"story","slug":"gorod-pod-lednikom","active":true},"/istorii/inzhener-dlya-osazhdennoy-kreposti/":{"content_id":"d1b82523-f623-4f6e-aaba-45100d9fd892","content_type":"story","slug":"inzhener-dlya-osazhdennoy-kreposti","active":true},"slug:inzhener-dlya-osazhdennoy-kreposti":{"content_id":"d1b82523-f623-4f6e-aaba-45100d9fd892","content_type":"story","slug":"inzhener-dlya-osazhdennoy-kreposti","active":true},"/istorii/kayuta-7/":{"content_id":"3a44d938-4a70-4dba-9644-625f203a01a2","content_type":"story","slug":"kayuta-7","active":true},"slug:kayuta-7":{"content_id":"3a44d938-4a70-4dba-9644-625f203a01a2","content_type":"story","slug":"kayuta-7","active":true},"/istorii/komnata-bez-otrazheniy/":{"content_id":"ba9ad1da-24b9-4d82-8b1f-b67f45c893c2","content_type":"story","slug":"komnata-bez-otrazheniy","active":true},"slug:komnata-bez-otrazheniy":{"content_id":"ba9ad1da-24b9-4d82-8b1f-b67f45c893c2","content_type":"story","slug":"komnata-bez-otrazheniy","active":true},"/istorii/kot-kotoryy-sdaval-kvartiru/":{"content_id":"58fd4d44-53f5-4e27-8589-d75e7e1d31d5","content_type":"story","slug":"kot-kotoryy-sdaval-kvartiru","active":true},"slug:kot-kotoryy-sdaval-kvartiru":{"content_id":"58fd4d44-53f5-4e27-8589-d75e7e1d31d5","content_type":"story","slug":"kot-kotoryy-sdaval-kvartiru","active":true},"/istorii/krasnaya-voda-pod-kilem/":{"content_id":"3900358d-4b7f-4d68-9956-f259fd8de334","content_type":"story","slug":"krasnaya-voda-pod-kilem","active":true},"slug:krasnaya-voda-pod-kilem":{"content_id":"3900358d-4b7f-4d68-9956-f259fd8de334","content_type":"story","slug":"krasnaya-voda-pod-kilem","active":true},"/istorii/kuryer-dlya-imperatora-drakonov/":{"content_id":"66ec419b-1227-4d7f-b493-46aa9736ed7f","content_type":"story","slug":"kuryer-dlya-imperatora-drakonov","active":true},"slug:kuryer-dlya-imperatora-drakonov":{"content_id":"66ec419b-1227-4d7f-b493-46aa9736ed7f","content_type":"story","slug":"kuryer-dlya-imperatora-drakonov","active":true},"/istorii/led-nad-bezdnoy/":{"content_id":"3dfb73ba-757d-443f-a708-ae5b8b8fbe37","content_type":"story","slug":"led-nad-bezdnoy","active":false},"slug:led-nad-bezdnoy":{"content_id":"3dfb73ba-757d-443f-a708-ae5b8b8fbe37","content_type":"story","slug":"led-nad-bezdnoy","active":false},"/istorii/marshrut-17/":{"content_id":"4d811adf-ba72-479d-a6be-1f0ba9d0f4b0","content_type":"story","slug":"marshrut-17","active":true},"slug:marshrut-17":{"content_id":"4d811adf-ba72-479d-a6be-1f0ba9d0f4b0","content_type":"story","slug":"marshrut-17","active":true},"/istorii/maska-dlya-chuzhogo-litsa/":{"content_id":"38ee9cc0-4f6d-49ad-bafa-05238924745c","content_type":"story","slug":"maska-dlya-chuzhogo-litsa","active":true},"slug:maska-dlya-chuzhogo-litsa":{"content_id":"38ee9cc0-4f6d-49ad-bafa-05238924745c","content_type":"story","slug":"maska-dlya-chuzhogo-litsa","active":true},"/istorii/nulevoy-passazhir/":{"content_id":"f6276976-be9f-4424-bc9e-e702e510962e","content_type":"story","slug":"nulevoy-passazhir","active":true},"slug:nulevoy-passazhir":{"content_id":"f6276976-be9f-4424-bc9e-e702e510962e","content_type":"story","slug":"nulevoy-passazhir","active":true},"/istorii/ofisnyy-klad/":{"content_id":"a5100218-842a-40e3-aec6-d26253011a86","content_type":"story","slug":"ofisnyy-klad","active":true},"slug:ofisnyy-klad":{"content_id":"a5100218-842a-40e3-aec6-d26253011a86","content_type":"story","slug":"ofisnyy-klad","active":true},"/istorii/ona-vyshla-na-stsenu-dvazhdy/":{"content_id":"080f2de5-be3c-4f76-bf51-ec1539cbc77d","content_type":"comic","slug":"ona-vyshla-na-stsenu-dvazhdy","active":true},"slug:ona-vyshla-na-stsenu-dvazhdy":{"content_id":"080f2de5-be3c-4f76-bf51-ec1539cbc77d","content_type":"comic","slug":"ona-vyshla-na-stsenu-dvazhdy","active":true},"/istorii/operatsiya-mertvyy-mayak/":{"content_id":"c668e547-9eef-40da-8e18-72d7a0c2c0d9","content_type":"story","slug":"operatsiya-mertvyy-mayak","active":true},"slug:operatsiya-mertvyy-mayak":{"content_id":"c668e547-9eef-40da-8e18-72d7a0c2c0d9","content_type":"story","slug":"operatsiya-mertvyy-mayak","active":true},"/istorii/ostrov-na-odin-priliv/":{"content_id":"7b7a5366-ad25-4a57-bac9-3d6ee8f04c6d","content_type":"story","slug":"ostrov-na-odin-priliv","active":true},"slug:ostrov-na-odin-priliv":{"content_id":"7b7a5366-ad25-4a57-bac9-3d6ee8f04c6d","content_type":"story","slug":"ostrov-na-odin-priliv","active":true},"/istorii/pansionat-tikhiy-uzhas/":{"content_id":"ff1c3fdc-1d73-4394-b315-a37b5139c748","content_type":"story","slug":"pansionat-tikhiy-uzhas","active":true},"slug:pansionat-tikhiy-uzhas":{"content_id":"ff1c3fdc-1d73-4394-b315-a37b5139c748","content_type":"story","slug":"pansionat-tikhiy-uzhas","active":true},"/istorii/passazhir-iz-poslednego-vagona/":{"content_id":"3a16efcd-3fdc-408a-8ceb-13649afade97","content_type":"story","slug":"passazhir-iz-poslednego-vagona","active":true},"slug:passazhir-iz-poslednego-vagona":{"content_id":"3a16efcd-3fdc-408a-8ceb-13649afade97","content_type":"story","slug":"passazhir-iz-poslednego-vagona","active":true},"/istorii/pechat-na-bagrovom-voske/":{"content_id":"21b702f1-b36a-4d64-891f-9bb0805ee28c","content_type":"comic","slug":"pechat-na-bagrovom-voske","active":true},"slug:pechat-na-bagrovom-voske":{"content_id":"21b702f1-b36a-4d64-891f-9bb0805ee28c","content_type":"comic","slug":"pechat-na-bagrovom-voske","active":true},"/istorii/planeta-bez-eha/":{"content_id":"5e95d5a1-a432-48a2-b546-9db322404481","content_type":"story","slug":"planeta-bez-eha","active":true},"slug:planeta-bez-eha":{"content_id":"5e95d5a1-a432-48a2-b546-9db322404481","content_type":"story","slug":"planeta-bez-eha","active":true},"/istorii/platforma-sever-9/":{"content_id":"0295b76e-185c-4b0e-b1b3-b6cd8d8b0956","content_type":"story","slug":"platforma-sever-9","active":true},"slug:platforma-sever-9":{"content_id":"0295b76e-185c-4b0e-b1b3-b6cd8d8b0956","content_type":"story","slug":"platforma-sever-9","active":true},"/istorii/pod-kamnem-ra/":{"content_id":"70b5df43-bad2-478e-8657-abb82eb30529","content_type":"story","slug":"pod-kamnem-ra","active":false},"slug:pod-kamnem-ra":{"content_id":"70b5df43-bad2-478e-8657-abb82eb30529","content_type":"story","slug":"pod-kamnem-ra","active":false},"/istorii/poezd-cherez-krasnuyu-pustynyu/":{"content_id":"d9d447d7-6c60-41ab-8986-9347b975e4ed","content_type":"story","slug":"poezd-cherez-krasnuyu-pustynyu","active":true},"slug:poezd-cherez-krasnuyu-pustynyu":{"content_id":"d9d447d7-6c60-41ab-8986-9347b975e4ed","content_type":"story","slug":"poezd-cherez-krasnuyu-pustynyu","active":true},"/istorii/poslednee-mesto-za-stolom/":{"content_id":"98a24fb3-7d25-4905-88e4-2e9f6e3aac80","content_type":"story","slug":"poslednee-mesto-za-stolom","active":true},"slug:poslednee-mesto-za-stolom":{"content_id":"98a24fb3-7d25-4905-88e4-2e9f6e3aac80","content_type":"story","slug":"poslednee-mesto-za-stolom","active":true},"/istorii/posledniy-kadr-strima/":{"content_id":"d97efa36-69a1-4349-bb80-0fe632952eb3","content_type":"story","slug":"posledniy-kadr-strima","active":true},"slug:posledniy-kadr-strima":{"content_id":"d97efa36-69a1-4349-bb80-0fe632952eb3","content_type":"story","slug":"posledniy-kadr-strima","active":true},"/istorii/posledniy-lift-bashni-orion/":{"content_id":"537d0df4-a90c-41c3-9cea-314c45af73c3","content_type":"story","slug":"posledniy-lift-bashni-orion","active":true},"slug:posledniy-lift-bashni-orion":{"content_id":"537d0df4-a90c-41c3-9cea-314c45af73c3","content_type":"story","slug":"posledniy-lift-bashni-orion","active":true},"/istorii/posledniy-reys-severnoy-chayki/":{"content_id":"1b64b5b2-305f-4d1d-b40f-29651d986968","content_type":"story","slug":"posledniy-reys-severnoy-chayki","active":true},"slug:posledniy-reys-severnoy-chayki":{"content_id":"1b64b5b2-305f-4d1d-b40f-29651d986968","content_type":"story","slug":"posledniy-reys-severnoy-chayki","active":true},"/istorii/posledniy-son-androida/":{"content_id":"afeec6b0-7751-4c17-8c28-c7408741d1a2","content_type":"story","slug":"posledniy-son-androida","active":true},"slug:posledniy-son-androida":{"content_id":"afeec6b0-7751-4c17-8c28-c7408741d1a2","content_type":"story","slug":"posledniy-son-androida","active":true},"/istorii/sedmoy-vodopad/":{"content_id":"3188e386-2acb-4dfb-9db4-565df6bc99a0","content_type":"story","slug":"sedmoy-vodopad","active":true},"slug:sedmoy-vodopad":{"content_id":"3188e386-2acb-4dfb-9db4-565df6bc99a0","content_type":"story","slug":"sedmoy-vodopad","active":true},"/istorii/sisadmin-pri-dvore-magov/":{"content_id":"e85d64a2-4d5b-4a8c-b8bd-d7b99426dff8","content_type":"story","slug":"sisadmin-pri-dvore-magov","active":true},"slug:sisadmin-pri-dvore-magov":{"content_id":"e85d64a2-4d5b-4a8c-b8bd-d7b99426dff8","content_type":"story","slug":"sisadmin-pri-dvore-magov","active":true},"/istorii/spisok-priglashennyh/":{"content_id":"64a7411b-bbae-41ca-bc14-bb01171fab37","content_type":"story","slug":"spisok-priglashennyh","active":true},"slug:spisok-priglashennyh":{"content_id":"64a7411b-bbae-41ca-bc14-bb01171fab37","content_type":"story","slug":"spisok-priglashennyh","active":true},"/istorii/stantsiya-kotoraya-molchala/":{"content_id":"cb28a149-93e7-4168-8078-1e07ded174bb","content_type":"story","slug":"stantsiya-kotoraya-molchala","active":true},"slug:stantsiya-kotoraya-molchala":{"content_id":"cb28a149-93e7-4168-8078-1e07ded174bb","content_type":"story","slug":"stantsiya-kotoraya-molchala","active":true},"/istorii/sukhoy-grom/":{"content_id":"04e49803-b395-4d42-9bb1-1b0a0f3ca51d","content_type":"story","slug":"sukhoy-grom","active":false},"slug:sukhoy-grom":{"content_id":"04e49803-b395-4d42-9bb1-1b0a0f3ca51d","content_type":"story","slug":"sukhoy-grom","active":false},"/istorii/svadba-s-dostavkoy/":{"content_id":"601ca384-90ac-4a5d-87f1-30e7436e7fc8","content_type":"story","slug":"svadba-s-dostavkoy","active":true},"slug:svadba-s-dostavkoy":{"content_id":"601ca384-90ac-4a5d-87f1-30e7436e7fc8","content_type":"story","slug":"svadba-s-dostavkoy","active":true},"/istorii/teatr-kotoryy-igraet-posle-zakrytiya/":{"content_id":"42bee4e7-6ec6-4288-8ec6-fef860089caf","content_type":"story","slug":"teatr-kotoryy-igraet-posle-zakrytiya","active":true},"slug:teatr-kotoryy-igraet-posle-zakrytiya":{"content_id":"42bee4e7-6ec6-4288-8ec6-fef860089caf","content_type":"story","slug":"teatr-kotoryy-igraet-posle-zakrytiya","active":true},"/istorii/tropa-zolotogo-yaguara/":{"content_id":"5cb4c76a-6fb7-4bb1-bd85-34dbda115829","content_type":"story","slug":"tropa-zolotogo-yaguara","active":true},"slug:tropa-zolotogo-yaguara":{"content_id":"5cb4c76a-6fb7-4bb1-bd85-34dbda115829","content_type":"story","slug":"tropa-zolotogo-yaguara","active":true},"/istorii/tsena-vtoroy-pechati/":{"content_id":"69be6467-f50d-4663-832a-31c2fd76d309","content_type":"story","slug":"tsena-vtoroy-pechati","active":true},"slug:tsena-vtoroy-pechati":{"content_id":"69be6467-f50d-4663-832a-31c2fd76d309","content_type":"story","slug":"tsena-vtoroy-pechati","active":true},"/istorii/veter-nad-tortugoy/":{"content_id":"e63561d6-09fe-45ed-8aba-b18599be7cd7","content_type":"story","slug":"veter-nad-tortugoy","active":false},"slug:veter-nad-tortugoy":{"content_id":"e63561d6-09fe-45ed-8aba-b18599be7cd7","content_type":"story","slug":"veter-nad-tortugoy","active":false},"/istorii/yurist-v-korolevstve-bez-zakonov/":{"content_id":"a6856a5d-3f8d-4a47-aab2-63bd39ce858b","content_type":"story","slug":"yurist-v-korolevstve-bez-zakonov","active":true},"slug:yurist-v-korolevstve-bez-zakonov":{"content_id":"a6856a5d-3f8d-4a47-aab2-63bd39ce858b","content_type":"story","slug":"yurist-v-korolevstve-bez-zakonov","active":true},"/istorii/zoloto-chernoy-marii/":{"content_id":"c59b19f8-bc4f-4ffd-8892-f75eaece8042","content_type":"story","slug":"zoloto-chernoy-marii","active":true},"slug:zoloto-chernoy-marii":{"content_id":"c59b19f8-bc4f-4ffd-8892-f75eaece8042","content_type":"story","slug":"zoloto-chernoy-marii","active":true}};
  var PLACEMENTS = new Set(["R-A-19563496-3","R-A-19563496-4","R-A-19563496-5","R-A-19563496-6","R-A-19563496-7","R-A-19563496-8","R-A-19563496-9","R-A-19563496-10","R-A-19563496-11","R-A-19563496-12","R-A-19563496-13","R-A-19563496-14"]);
  var ALLOWLIST = Object.freeze({
    yclid:128, utm_source:128, utm_medium:64, utm_campaign:256,
    utm_content:256, utm_term:256, campaign_id:128, ad_id:128,
    group_id:128, criterion_id:128, phrase_id:128, keyword_id:128
  });
  var PAID_MEDIA = new Set(["cpc","ppc","paid","paidsearch","paid_search","display"]);

  function safeAgent(reason, siteId) {
    return Object.freeze({
      site_id:siteId || "dilivox", schema_version:SCHEMA_VERSION,
      deployment_version:DEPLOYMENT_VERSION, enabled:false,
      health:{ok:false, state:"SAFE_NOOP", reason:reason || "disabled"},
      getContext:function(){return null;},
      buildEventContext:function(){return null;}
    });
  }
  function clean(value, max) {
    if (typeof value !== "string") return null;
    var normalized=value.normalize("NFKC").replace(/[\u0000-\u001f\u007f]/g,"").trim().slice(0,max);
    return normalized || null;
  }
  function randomId(win) {
    try {
      var bytes=new Uint8Array(16); win.crypto.getRandomValues(bytes);
      bytes[6]=(bytes[6]&15)|64; bytes[8]=(bytes[8]&63)|128;
      var h=Array.from(bytes,function(b){return b.toString(16).padStart(2,"0");}).join("");
      return h.slice(0,8)+"-"+h.slice(8,12)+"-"+h.slice(12,16)+"-"+h.slice(16,20)+"-"+h.slice(20);
    } catch (_) { return null; }
  }
  function storageGet(storage,key,now) {
    try {
      var raw=storage && storage.getItem(key); if(!raw) return null;
      var value=JSON.parse(raw);
      if (!value || typeof value !== "object" || (value.expires_at && value.expires_at <= now)) {
        if(storage) storage.removeItem(key); return null;
      }
      return value;
    } catch (_) { try { if(storage) storage.removeItem(key); } catch(__){} return null; }
  }
  function storageSet(storage,key,value) {
    try { if(storage) storage.setItem(key,JSON.stringify(value)); return true; }
    catch (_) { return false; }
  }
  function resolveContent(doc, location) {
    try {
      var story=doc && doc.querySelector("[data-dv-story-slug]");
      var slug=story && clean(story.getAttribute("data-dv-story-slug"),128);
      if(slug && CONTENT["slug:"+slug]) return CONTENT["slug:"+slug];
      var path=(location && location.pathname) || "/";
      if(path.length>1 && !path.endsWith("/")) path+="/";
      if(CONTENT[path]) return CONTENT[path];
      var page=doc && doc.querySelector("[data-dv-page]");
      var pageName=page && clean(page.getAttribute("data-dv-page"),64);
      return pageName && CONTENT["slug:"+pageName] || null;
    } catch (_) { return null; }
  }
  function capture(url, contentId, now, win) {
    var parsed; try { parsed=new win.URL(url); } catch (_) { return null; }
    var params={};
    Object.keys(ALLOWLIST).forEach(function(key){
      var value=clean(parsed.searchParams.get(key),ALLOWLIST[key]); if(value) params[key]=value;
    });
    var paid=Boolean(params.yclid || params.campaign_id || params.ad_id || params.group_id ||
      (params.utm_medium && PAID_MEDIA.has(params.utm_medium.toLowerCase())) ||
      (params.utm_source && /^(yandex|direct)$/i.test(params.utm_source) && params.utm_campaign));
    if(!paid) return null;
    var id=randomId(win); if(!id) return null;
    return {schema_version:"1.0", acquisition_id:id, cohort_ref:"acq:"+id,
      landing_content_id:contentId || null, acquired_at:now, expires_at:null, params:params};
  }
  function attribution(win, content, options, now) {
    var ttl=Math.min(Math.max(Number(options.attributionTtlMs)||MAX_TTL_MS,1),MAX_TTL_MS);
    var current=storageGet(win.sessionStorage,"pe_acquisition_v1",now) ||
      storageGet(win.localStorage,"pe_acquisition_v1",now);
    var fresh=capture(win.location.href,content && content.content_id,now,win);
    if(fresh) {
      fresh.expires_at=now+ttl; current=fresh;
      storageSet(win.sessionStorage,"pe_acquisition_v1",fresh);
      if(options.persistAttribution) storageSet(win.localStorage,"pe_acquisition_v1",fresh);
    } else if(current) {
      storageSet(win.sessionStorage,"pe_acquisition_v1",current);
    }
    return current;
  }
  function session(win,now) {
    var value=storageGet(win.sessionStorage,"pe_session_v1",now);
    if(value) return value;
    var id=randomId(win); if(!id) return null;
    value={session_id:id,created_at:now}; storageSet(win.sessionStorage,"pe_session_v1",value);
    return value;
  }
  function returnIdentity(win,options,now) {
    if(!options.enableReturnId || !options.privacyReviewApproved) return null;
    var ttl=Math.min(Math.max(Number(options.returnTtlMs)||MAX_TTL_MS,1),MAX_TTL_MS);
    var value=storageGet(win.localStorage,"pe_return_v1",now);
    if(value) return value;
    var id=randomId(win); if(!id) return null;
    value={return_id:id,created_at:now,expires_at:now+ttl};
    storageSet(win.localStorage,"pe_return_v1",value); return value;
  }
  function experiment(options) {
    var exp=clean(options.experiment_id,64), variant=clean(options.variant_id,64);
    var valid=function(x){return !x || /^[A-Za-z0-9._:-]{1,64}$/.test(x);};
    var killed=Boolean(options.globalKillSwitch || (exp && (options.experimentKillSwitches||[]).includes(exp)));
    if(killed || !valid(exp) || !valid(variant) || Boolean(exp)!==Boolean(variant)) return null;
    return exp ? {experiment_id:exp,variant_id:variant,exposure_eligible:true} : null;
  }
  function placementIds(doc) {
    try {
      return Array.from(doc.querySelectorAll("[data-dv-ad-block]"))
        .map(function(node){return node.getAttribute("data-dv-ad-block");})
        .filter(function(id,index,all){return PLACEMENTS.has(id) && all.indexOf(id)===index;});
    } catch (_) { return []; }
  }
  function createSiteAgent(win, adapter, options) {
    options=options||{};
    if(options.globalKillSwitch || win.__PROFIT_ENGINE_SITE_AGENT_DISABLED__ === true) return safeAgent("global_kill_switch",adapter.site_id);
    try {
      var now=(options.now || Date.now)();
      var content=adapter.resolveContent(win.document,win.location);
      var sess=session(win,now);
      var acq=attribution(win,content,options,now);
      var ret=returnIdentity(win,options,now);
      var exp=experiment(options);
      var placements=adapter.placementIds(win.document);
      var base={site_id:adapter.site_id,schema_version:SCHEMA_VERSION,deployment_version:DEPLOYMENT_VERSION,
        content_id:content && content.content_id || null,page_type:content && content.content_type || null,
        session_ref:sess && sess.session_id || null,return_ref:ret && ret.return_id || null,
        acquisition_ref:acq && acq.acquisition_id || null,cohort_ref:acq && acq.cohort_ref || null,
        experiment_id:exp && exp.experiment_id || null,variant_id:exp && exp.variant_id || null,
        placement_ids:placements};
      return Object.freeze({
        site_id:adapter.site_id,schema_version:SCHEMA_VERSION,deployment_version:DEPLOYMENT_VERSION,
        enabled:true,health:{ok:true,state:content?"READY":"DEGRADED_UNKNOWN_CONTENT"},
        attribution:acq,session:sess,experiment:exp,placements:placements,
        getContext:function(){return Object.assign({},base);},
        buildEventContext:function(extra){
          extra=extra||{};
          return Object.assign({},base,{event_schema_version:EVENT_SCHEMA_VERSION,
            source_content_id:extra.source_content_id||null,
            destination_content_id:extra.destination_content_id||null,
            placement_id:extra.placement_id && PLACEMENTS.has(extra.placement_id) ? extra.placement_id : null,
            timestamp:new Date((options.now || Date.now)()).toISOString()});
        }
      });
    } catch (_) { return safeAgent("runtime_failure",adapter.site_id); }
  }
  var DILIVOX_ADAPTER=Object.freeze({site_id:"dilivox",resolveContent:resolveContent,placementIds:placementIds});
  function createDilivoxSiteAgent(win, options) { return createSiteAgent(win,DILIVOX_ADAPTER,options); }
  return Object.freeze({ALLOWLIST:ALLOWLIST,MAX_TTL_MS:MAX_TTL_MS,resolveContent:resolveContent,
    captureAttribution:capture,createSiteAgent:createSiteAgent,
    createDilivoxSiteAgent:createDilivoxSiteAgent,DILIVOX_ADAPTER:DILIVOX_ADAPTER,safeAgent:safeAgent});
});


(function(root){
  "use strict";
  var TYPES=new Set(["page_view_site","story_open","story_progress_25","story_progress_50","story_progress_75","version_section_seen","version_selected","reveal_opened","story_completed","next_story_seen","next_story_clicked","catalog_opened","return_visit","session_end_summary","experiment_exposure","experiment_conversion"]);
  var PROPS={version_selected:new Set(["choice_ref","is_correct"]),session_end_summary:new Set(["duration_bucket","event_count"]),experiment_conversion:new Set(["source_event_id","conversion_key"])};
  var MAX_EVENT=8192,MAX_BATCH=65536,MAX_QUEUE=50,TTL=86400000,MAX_RETRY=3;
  function hash(s){var h1=0x811c9dc5,h2=0x9e3779b9;for(var i=0;i<s.length;i++){h1=Math.imul(h1^s.charCodeAt(i),16777619);h2=Math.imul(h2^s.charCodeAt(i),2246822519);}return ((h1>>>0).toString(16).padStart(8,"0")+(h2>>>0).toString(16).padStart(8,"0"));}
  function uuid(win){try{return win.crypto.randomUUID?win.crypto.randomUUID():(function(){var a=new Uint8Array(16);win.crypto.getRandomValues(a);a[6]=a[6]&15|64;a[8]=a[8]&63|128;var h=Array.from(a,x=>x.toString(16).padStart(2,"0")).join("");return h.slice(0,8)+"-"+h.slice(8,12)+"-"+h.slice(12,16)+"-"+h.slice(16,20)+"-"+h.slice(20);})();}catch(_){return null;}}
  function cleanProperties(type,input){var allowed=PROPS[type]||new Set(),out={};Object.keys(input||{}).forEach(function(k){if(allowed.has(k)){var v=input[k];if(typeof v==="boolean"||typeof v==="number"||(typeof v==="string"&&v.length<=128))out[k]=v;}});return out;}
  function Builder(win,agent,health){this.win=win;this.agent=agent;this.health=health;this.once=new Set();}
  Builder.prototype.create=function(type,instanceKey,extra){
    try{
      if(!TYPES.has(type)||this.win.__PROFIT_ENGINE_EVENT_DISPATCH_DISABLED__===true)return null;
      var ctx=this.agent.getContext(); if(!ctx){this.health.unresolved_content_identity++;return null;}
      var singleton=[ctx.schema_version,ctx.site_id,ctx.session_ref,ctx.content_id,type,instanceKey||"singleton"].join("|");
      var key="evt_"+hash(singleton); if(this.once.has(key)){this.health.duplicates++;return null;} this.once.add(key);
      var event={schema_version:"1.0",event_id:uuid(this.win),idempotency_key:key,event_type:type,occurred_at:new Date().toISOString(),site_id:ctx.site_id,content_id:ctx.content_id,content_type:ctx.page_type,session_id:ctx.session_ref,acquisition_id:ctx.acquisition_ref,cohort_ref:ctx.cohort_ref,experiment_id:ctx.experiment_id,variant_id:ctx.variant_id,placement_id:extra&&extra.placement_id||null,source_content_id:extra&&extra.source_content_id||null,destination_content_id:extra&&extra.destination_content_id||null,deployment_version:"task-006-unpublished-v1",properties:cleanProperties(type,extra&&extra.properties)};
      if(!event.event_id||JSON.stringify(event).length>MAX_EVENT){this.health.rejected++;return null;} this.health.created++;return event;
    }catch(_){this.health.instrumentation_errors++;return null;}
  };
  function Queue(options,health){options=options||{};this.items=[];this.transport=options.transport||null;this.now=options.now||Date.now;this.health=health;this.killed=Boolean(options.killSwitch);this.max=MAX_QUEUE;}
  Queue.prototype.push=function(event){if(!event||this.killed)return false;this.prune();if(this.items.length>=this.max){this.items.shift();this.health.dropped++;this.health.overflow++;}this.items.push({event:event,created_at:this.now(),attempts:0});this.health.queue_depth=this.items.length;return true;};
  Queue.prototype.prune=function(){var now=this.now(),before=this.items.length;this.items=this.items.filter(x=>now-x.created_at<=TTL);this.health.dropped+=before-this.items.length;};
  Queue.prototype.flush=async function(){if(this.killed||!this.transport||!this.items.length)return {status:"disabled_or_empty"};this.prune();var batch=[],size=0;for(const item of this.items){var n=JSON.stringify(item.event).length;if(size+n>MAX_BATCH)break;batch.push(item);size+=n;}if(!batch.length)return {status:"empty"};for(var attempt=1;attempt<=MAX_RETRY;attempt++){try{var ok=await this.transport(batch.map(x=>x.event));if(ok){this.items.splice(0,batch.length);this.health.sent+=batch.length;this.health.acked+=batch.length;this.health.queue_depth=this.items.length;return {status:"acked",attempts:attempt};}}catch(_){this.health.delivery_failures++;} }return {status:"failed",attempts:MAX_RETRY};};
  function Controller(win,agent,options){options=options||{};this.health={created:0,sent:0,acked:0,rejected:0,dropped:0,duplicates:0,delivery_failures:0,queue_depth:0,overflow:0,unresolved_content_identity:0,instrumentation_errors:0,js_error_count:0,site_agent_health:agent.health.state,dispatch_killed:Boolean(options.dispatchKillSwitch)};this.builder=new Builder(win,agent,this.health);this.queue=new Queue({transport:options.transport,now:options.now,killSwitch:options.dispatchKillSwitch},this.health);this.agent=agent;this.revealOpen=false;this.started=Date.now();}
  Controller.prototype.emit=function(type,key,extra){if(this.queue.killed)return null;var e=this.builder.create(type,key,extra);if(e)this.queue.push(e);return e;};
  Controller.prototype.pageLoad=function(hasStoryBody){this.emit("page_view_site","page-load");if(hasStoryBody&&this.agent.getContext().content_id)this.emit("story_open","story-body");};
  Controller.prototype.progress=function(ratio){[25,50,75].forEach(n=>{if(ratio>=n/100)this.emit("story_progress_"+n,String(n));});};
  Controller.prototype.progressFromGeometry=function(rect,viewportHeight){var ratio=Math.max(0,Math.min(1,(viewportHeight-rect.top)/Math.max(rect.height,1)));this.progress(ratio);return ratio;};
  Controller.prototype.choiceSectionVisible=function(fraction){if(fraction>=.5)this.emit("version_section_seen","choice-visible");};
  Controller.prototype.selectChoice=function(ref,isCorrect,trusted){if(trusted)this.emit("version_selected",String(ref),{properties:{choice_ref:String(ref).slice(0,64),is_correct:Boolean(isCorrect)}});};
  Controller.prototype.reveal=function(open,visibleFraction){if(open&&!this.revealOpen){this.revealOpen=true;this.emit("reveal_opened","reveal");}if(this.revealOpen&&visibleFraction>=.5)this.emit("story_completed","reveal-viewed");};
  Controller.prototype.nextSeen=function(dest,fraction){if(fraction>=.5)this.emit("next_story_seen",dest,{source_content_id:this.agent.getContext().content_id,destination_content_id:dest});};
  Controller.prototype.nextClicked=function(dest,trusted){if(trusted)this.emit("next_story_clicked",dest,{source_content_id:this.agent.getContext().content_id,destination_content_id:dest});};
  Controller.prototype.catalog=function(trusted){if(trusted)this.emit("catalog_opened","catalog");};
  Controller.prototype.exposure=function(actual){if(actual&&this.agent.experiment)this.emit("experiment_exposure",this.agent.experiment.experiment_id+"|"+this.agent.experiment.variant_id);};
  Controller.prototype.conversion=function(mapping){if(mapping&&mapping.approved===true&&mapping.source_event_id)this.emit("experiment_conversion",mapping.conversion_key,{properties:{source_event_id:mapping.source_event_id,conversion_key:mapping.conversion_key}});};
  Controller.prototype.returnVisit=function(){if(this.agent.getContext().return_ref)this.emit("return_visit","return");};
  Controller.prototype.summary=function(){var seconds=Math.max(0,Math.floor((Date.now()-this.started)/1000));return this.emit("session_end_summary","end",{properties:{duration_bucket:seconds<60?"lt_1m":seconds<300?"1_5m":"gte_5m",event_count:this.health.created}});};
  Controller.prototype.recordError=function(type,signature){this.health.js_error_count++;this.health.last_error_type=String(type||"unknown").slice(0,32);this.health.last_error_signature="err_"+hash(String(signature||type||"unknown"));};
  Controller.prototype.recordPerformance=function(values){values=values||{};this.health.navigation_ms=Math.max(0,Math.round(Number(values.navigation_ms)||0));this.health.lcp_ms=Math.max(0,Math.round(Number(values.lcp_ms)||0));this.health.cls=Math.max(0,Math.min(100,Number(values.cls)||0));this.health.long_task_count=Math.max(0,Math.round(Number(values.long_task_count)||0));};
  function wireDom(win,c){
    var d=win.document,text=d.querySelector("[data-dv-story-text]");c.pageLoad(Boolean(text));
    var onScroll=function(){try{if(text)c.progressFromGeometry(text.getBoundingClientRect(),win.innerHeight||0);}catch(_){c.health.instrumentation_errors++;}};
    win.addEventListener&&win.addEventListener("scroll",onScroll,{passive:true});onScroll();
    d.addEventListener&&d.addEventListener("click",function(ev){try{var choice=ev.target.closest&&ev.target.closest("[data-dv-choice]");if(choice)c.selectChoice(choice.getAttribute("data-dv-choice")||"choice",choice.getAttribute("data-dv-correct")==="true",ev.isTrusted);var nav=ev.target.closest&&ev.target.closest("[data-dv-goal]");if(nav&&ev.isTrusted){var goal=nav.getAttribute("data-dv-goal");if(goal==="next-story"){var target=root.ProfitEngineSiteAgent.resolveContent(null,new win.URL(nav.href,win.location.href));c.nextClicked(target&&target.content_id,true);}if(["back-to-stories","home-to-stories","catalog-open"].includes(goal))c.catalog(true);}}catch(_){c.health.instrumentation_errors++;}});
    if(win.IntersectionObserver){var io=new win.IntersectionObserver(function(entries){entries.forEach(function(e){var n=e.target;if(n.matches&&n.matches("[data-dv-choice]"))c.choiceSectionVisible(e.intersectionRatio);if(n.matches&&n.matches("[data-dv-reveal]"))c.reveal(!n.hidden&&n.getAttribute("aria-hidden")!=="true",e.intersectionRatio);if(n.matches&&n.matches('[data-dv-goal="next-story"]')){var t=root.ProfitEngineSiteAgent.resolveContent(null,new win.URL(n.href,win.location.href));c.nextSeen(t&&t.content_id,e.intersectionRatio);}});},{threshold:[.5]});d.querySelectorAll&&d.querySelectorAll('[data-dv-choice],[data-dv-reveal],[data-dv-goal="next-story"]').forEach(n=>io.observe(n));}
    win.addEventListener&&win.addEventListener("pagehide",function(){c.summary();void c.queue.flush();},{capture:true});
  }
  function install(win,options){try{var agent=root.ProfitEngineSiteAgent.createDilivoxSiteAgent(win,options&&options.siteAgent);var c=new Controller(win,agent,options);if(options&&options.autoStart)wireDom(win,c);if(options&&options.experimentActuallyRendered)c.exposure(true);return c;}catch(_){return {health:{instrumentation_errors:1},emit:function(){return null;},queue:{flush:async function(){return {status:"failed_open"};}}};}}
  root.ProfitEngineEvents=Object.freeze({TYPES:TYPES,MAX_EVENT:MAX_EVENT,MAX_BATCH:MAX_BATCH,MAX_QUEUE:MAX_QUEUE,TTL:TTL,MAX_RETRY:MAX_RETRY,Builder:Builder,Queue:Queue,Controller:Controller,install:install});
})(typeof globalThis!=="undefined"?globalThis:this);
