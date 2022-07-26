import xml.etree.ElementTree as ET


def makemsg(daomeidan: str, describe: str, img_src: str, linked_url: str = "") -> str:
    msg = ET.Element("msg")
    # set msg.property
    msg.set("serviceID", "1")
    msg.set("templateID", "1")
    msg.set("action", "web")
    msg.set("brief", f"{daomeidan}")
    msg.set("sourceMsgId", "0")
    msg.set("url", linked_url)
    msg.set("flag", "0")
    msg.set("adverSign", "0")
    msg.set("multiMsgFlag", "0")
    item = ET.SubElement(msg, "item")
    item.set("layout", "2")  # 排版
    item.set("advertiser_id", "0")
    item.set("aid", "0")
    pic = ET.SubElement(item, "picture")
    pic.set("cover", img_src)
    pic.set("w", "0")
    pic.set("h", "0")
    title = ET.SubElement(item, "title")
    title.text = f"{daomeidan}"
    summary = ET.SubElement(item, "summary")
    summary.text = describe
    source = ET.SubElement(msg, "source")

    # dump
    xml_str = ET.tostring(msg, encoding="utf-8",
                          xml_declaration=True).decode("utf-8")
    # CQCODE encapsulation
    cqcode = "[CQ:xml,data=" + xml_str + ",resid=]"
    return cqcode
