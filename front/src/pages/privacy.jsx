import React from 'react';

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-200 px-6 py-12 flex justify-center">
      <main className="w-full max-w-3xl space-y-8 font-sans">
        {/* Header */}
        <div className="border-b border-gray-800 pb-6">
          <h1 className="text-3xl font-bold tracking-tight text-white">Privacy Policy</h1>
          <p className="text-sm text-gray-400 mt-1">Last updated: October 2026</p>
        </div>

        {/* Content Section */}
        <section className="space-y-6 text-gray-300 leading-relaxed text-sm md:text-base">
          <div>
            <h2 className="text-xl font-semibold text-white mb-2">1. Introduction</h2>
            <p>
              Welcome to Kai. We respect your privacy and are committed to protecting your personal data. 
              This privacy policy will inform you as to how we look after your personal data when you visit 
              our application and tell you about your privacy rights and how the law protects you.
            </p>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white mb-2">2. Information We Collect</h2>
            <p className="mb-2">We may collect, use, store and transfer different kinds of personal data about you which we have grouped together as follows:</p>
            <ul className="list-disc pl-6 space-y-1 text-gray-400">
              <li><strong className="text-gray-300">Identity Data:</strong> Includes username, handle, or similar identifier.</li>
              <li><strong className="text-gray-300">Contact Data:</strong> Includes email address and communication preferences.</li>
              <li><strong className="text-gray-300">Technical Data:</strong> Includes internet protocol (IP) address, browser type and version, time zone setting, and operating system.</li>
              <li><strong className="text-gray-300">Usage Data:</strong> Includes information about how you use our application, AI prompts, and tool integrations.</li>
            </ul>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white mb-2">3. How We Use Your Information</h2>
            <p>
              We will only use your personal data when the law allows us to. Most commonly, we will use your personal data in the following circumstances:
            </p>
            <ul className="list-disc pl-6 space-y-1 text-gray-400 mt-2">
              <li>To provide and maintain our service, including managing your AI assistant integrations.</li>
              <li>To notify you about changes to our service.</li>
              <li>To provide customer support and troubleshoot technical issues.</li>
              <li>To gather analysis or valuable information so that we can improve our service.</li>
            </ul>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white mb-2">4. Data Security</h2>
            <p>
              We have put in place appropriate security measures to prevent your personal data from being accidentally lost, used, or accessed in an unauthorized way, altered, or disclosed. In addition, we limit access to your personal data to those employees, agents, contractors, and other third parties who have a business need to know.
            </p>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white mb-2">5. Contact Us</h2>
            <p>
              If you have any questions about this privacy policy or our privacy practices, please contact us at support@kai.local.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
};