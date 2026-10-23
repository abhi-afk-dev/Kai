import React from "react";

export default function TermsOfService () {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-200 px-6 py-12 flex justify-center">
      <main className="w-full max-w-3xl space-y-8 font-sans">
        {/* Header */}
        <div className="border-b border-gray-800 pb-6">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Terms of Service
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Last updated: October 2026
          </p>
        </div>

        {/* Content Section */}
        <section className="space-y-6 text-gray-300 leading-relaxed text-sm md:text-base">
          <div>
            <h2 className="text-xl font-semibold text-white mb-2">
              1. Acceptance of Terms
            </h2>
            <p>
              By accessing or using Kai, you agree to be bound by these Terms of
              Service and all applicable laws and regulations. If you do not
              agree with any of these terms, you are prohibited from using or
              accessing this platform.
            </p>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white mb-2">
              2. Use License
            </h2>
            <p>
              Permission is granted to temporarily use Kai for personal,
              non-commercial transitory viewing and operational usage only. This
              grant of license does not transfer title, and under this license
              you may not:
            </p>
            <ul className="list-disc pl-6 space-y-1 text-gray-400 mt-2">
              <li>
                Modify or copy the materials or underlying source code without
                authorization.
              </li>
              <li>
                Use the materials for any commercial purpose or for any public
                display.
              </li>
              <li>
                Attempt to decompile or reverse engineer any software contained
                on Kai.
              </li>
              <li>
                Remove any copyright or other proprietary notations from the
                materials.
              </li>
            </ul>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white mb-2">
              3. User Accounts and Security
            </h2>
            <p>
              When you create an account with us, you must provide information
              that is accurate, complete, and current at all times. Failure to
              do so constitutes a breach of the Terms, which may result in
              immediate termination of your account on our service. You are
              responsible for safeguarding the credentials and API keys you use
              to access the service.
            </p>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white mb-2">
              4. Limitations of Liability
            </h2>
            <p>
              In no event shall Kai, nor its directors, employees, partners,
              agents, suppliers, or affiliates, be liable for any indirect,
              incidental, special, consequential or punitive damages, including
              without limitation, loss of profits, data, use, goodwill, or other
              intangible losses, resulting from your access to or use of or
              inability to access or use the service.
            </p>
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white mb-2">
              5. Changes to Terms
            </h2>
            <p>
              We reserve the right, at our sole discretion, to modify or replace
              these Terms at any time. What constitutes a material change will
              be determined at our sole discretion. By continuing to access or
              use our service after any revisions become effective, you agree to
              be bound by the revised terms.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
};
