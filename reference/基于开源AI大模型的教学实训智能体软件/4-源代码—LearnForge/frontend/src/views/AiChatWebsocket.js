import CryptoJS from "crypto-js";
import * as base64 from "base-64";

// Websocke配置


// 根据版本指定访问的领域
const vDomain = {
  "v1.1": "general",
  "v2.1": "generalv2",
  "v3.1": "generalv3",
  "v3.5": "generalv3.5"
};
// 会话项
/**
 * 鉴权URL生成
 * @param  config  配置信息
 * @returns url 鉴权URL
 */
export const getWebsocketUrl = (config) => {
  let url = `wss://spark-api.xf-yun.com/${config.VERSION}/chat`;
  let host = "spark-api.xf-yun.com"; // 修复：使用正确的API主机名
  let apiKeyName = "api_key";

  let date = new Date().toUTCString();

  let algorithm = "hmac-sha256";

  let headers = "host date request-line";

  // signature
  let signatureOrigin = `host: ${host}\ndate: ${date}\nGET /${config.VERSION}/chat HTTP/1.1`;
  let signatureSha = CryptoJS.HmacSHA256(signatureOrigin, config.APISecret);
  let signature = CryptoJS.enc.Base64.stringify(signatureSha);

  // authorization参数 组成
  let authorizationOrigin = `${apiKeyName}="${config.APIKey}", algorithm="${algorithm}", headers="${headers}", signature="${signature}"`;

  // authorization参数(base64编码的签名信息)生成
  let authorization = base64.encode(authorizationOrigin);
  url = `${url}?authorization=${authorization}&date=${encodeURI(date)}&host=${host}`;

  return url;
};

/**
 * 发送数据格式化
 * @param sendData
 * @param sendData
 * @returns (数据结构注解可参考本文件中interface WSReqParams)
 */
export const wsSendMsgFormat = (config, sendData) => {
  const formatData = {
    header: {
      app_id: config.APPID,
    },
    parameter: {
      chat: {
        domain: vDomain[config.VERSION],
        max_tokens: 2096,
      },
    },
    payload: {
      message: {
        text: sendData,
      },
    },
  };

  return formatData;
};
